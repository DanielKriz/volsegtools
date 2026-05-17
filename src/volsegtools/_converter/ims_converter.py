import logging
from pathlib import Path
from typing import List

import dask.array as da
import h5py as hdf
import numpy as np
import collections
import re

from volsegtools._core.data_kind import DataKind
from volsegtools._core.vector import Vector3
from volsegtools._core.unit_kind import unit_from_str
from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import DataSet, DataSetInfo
from volsegtools._model.working_store import WorkingStore
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


def _type_cast_attrs(attrs):
    """Converts relevant metadata to their underlying type.

    Metadata is relevant if it is used in processing.

    The metadata are stored as raw numpy byte arrays; thus they have to be
    first converted to string, so that we can use Python's built-in
    conversions. After that we have to typecase the important members
    of the metadata to their true, mostly numerical, type.
    """

    def to_str(x):
        return x.tobytes().decode("utf-8")

    attrs_dict = {k: to_str(attrs[k]) for k in attrs.keys()}

    attrs_dict["ExtMax0"] = float(attrs_dict["ExtMax0"])
    attrs_dict["ExtMax1"] = float(attrs_dict["ExtMax1"])
    attrs_dict["ExtMax2"] = float(attrs_dict["ExtMax2"])
    attrs_dict["ExtMin0"] = float(attrs_dict["ExtMin0"])
    attrs_dict["ExtMin1"] = float(attrs_dict["ExtMin1"])
    attrs_dict["ExtMin2"] = float(attrs_dict["ExtMin2"])
    attrs_dict["X"] = int(attrs_dict["X"])
    attrs_dict["Y"] = int(attrs_dict["Y"])
    attrs_dict["Z"] = int(attrs_dict["Z"])
    attrs_dict["Unit"] = unit_from_str(attrs_dict["Unit"])

    return attrs_dict


def _find_all_channels(ch_list: list, info: dict):
    Channel = collections.namedtuple(
        "Channel",
        ["namespace", "resolution", "time_frame", "channel_id", "metadata", "data"],
    )

    hdf_re = r"(?P<namespace>.*)\/DataSet\d*\/(?P<resolution>ResolutionLevel \d+)\/(?P<time_frame>TimePoint \d+)\/(?P<channel>Channel \d+)$"

    def _find_all(x, y):
        match = re.match(hdf_re, x.strip())
        if match is not None:
            ch_list.append(
                Channel(
                    match.group("namespace"),
                    int(match.group("resolution")[-1]),
                    int(match.group("time_frame")[-1]),
                    int(match.group("channel")[-1]),
                    info[match.group("namespace")],
                    y["Data"],
                )
            )
            vst_logger.debug(
                "Added new channel: {}".format(_channel_to_str(ch_list[-1]))
            )

    return _find_all


def _channel_to_str(channel):
    return f"{channel.namespace} (R: {channel.resolution}, T: {channel.time_frame}, C:{channel.channel_id},)"


def _find_image_info(info: dict):
    hdf_re = r"(?P<namespace>.*)\/DataSet.*Image$"

    def _find_all(x, y):
        match = re.match(hdf_re, x.strip())
        if match is not None:
            info[match.group("namespace")] = _type_cast_attrs(y.attrs)

    return _find_all


class ImarisConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["ims"]

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    @staticmethod
    def calculate_voxel_size(input_info) -> Vector3:
        """Calculates voxel size from info of some Imaris Bitplane file.

        The voxel size is not provided in the form of some attribute, but it
        has to be calculated from the metadata as follows:

        1. We take the origin (minimum) of the data extent.
        2. We take the maximum extent.
        3. We calculate the difference between the max and min extent.
        4. We divide the differences by the number of samples in given axis.
        """
        # FIXME: This has to be refactored to work with multiple files
        info = next(iter(input_info.values()))
        return Vector3(
            100 * ((info["ExtMax0"] - info["ExtMin0"]) / info["X"]),
            100 * ((info["ExtMax1"] - info["ExtMin1"]) / info["Y"]),
            100 * ((info["ExtMax2"] - info["ExtMin2"]) / info["Z"]),
        )

    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        if not input_path.exists():
            raise RuntimeError(
                f"You have to provide a valid file, {input_path} does not exists"
            )
        vst_logger.info(f"... converting '{input_path}'")

        file = hdf.File(input_path, "r")

        dataset_info = dict()
        file.visititems(_find_image_info(dataset_info))
        voxel_size = ImarisConverter.calculate_voxel_size(dataset_info)

        channels = []
        file.visititems(_find_all_channels(channels, dataset_info))

        metadata = channels[0].metadata
        shape = channels[0].data.shape

        info = DataSetInfo(
            filename=input_path.name,
            resolution=0,
            axis_order=Vector3(0, 1, 2),
            voxel_size=voxel_size,
            origin=Vector3(
                metadata["ExtMin0"], metadata["ExtMin1"], metadata["ExtMin2"]
            ),
            id=input_path.name,
            kind=DataKind.VOLUME,
            lattice_shape=Vector3(
                shape[0],
                shape[1],
                shape[2],
            ),
        )

        data_set = DataSet(WorkingStore.instance.data_store, info)

        encountered_channel_ids = []

        for channel_info in channels:
            if not channel_info.resolution == 0:
                continue

            metadata = channel_info.metadata
            if not (0 <= channel_info.time_frame < len(data_set.time_frames)):
                for _ in range(channel_info.time_frame + 1 - len(data_set.time_frames)):
                    data_set.add_time_frame()

            # It is still not clear what is stored in the Imaris file,
            # sometimes some new channel appears, we have to store it somehow
            # so we find a place for it.
            idx = channel_info.channel_id
            while idx in encountered_channel_ids:
                idx += 1

            channel = data_set.time_frames[channel_info.time_frame].add_channel(idx)
            encountered_channel_ids.append(idx)

            dask_data = da.from_array(channel_info.data)
            dask_data = dask_data.transpose((2, 1, 0))
            dask_data = dask_data.rechunk("auto")

            # NOTE it might happen that different type would appear
            dask_data = dask_data.astype(np.float32)

            channel.set_data(dask_data, DaskBackend)

        file.close()

        return [data_set]

    async def convert_segmentation(self, input_path: Path) -> List[DataSet]:
        return await self.convert_volume(input_path)

    async def collect_annotations(self, input_path) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError
