import logging
import shutil
import sys
from pathlib import Path
from typing import List

import typer
from typing_extensions import Annotated

import volsegtools as vst

app = typer.Typer()


@app.command()
def run(
    volume_source: Annotated[
        List[Path], typer.Option(help="Specifies a path to volumetric data.")
    ] = [],
    segmentation_source: Annotated[
        List[Path], typer.Option(help="Specifies a path to segmentation data.")
    ] = [],
    workdir: Annotated[
        Path,
        typer.Option(help="Remove temporal Zarr store created during downsampling."),
    ] = Path.cwd(),
    rm_tmp: Annotated[
        bool,
        typer.Option(help="Remove temporal Zarr store created during downsampling."),
    ] = False,
    overwrite_tmp: Annotated[
        bool, typer.Option(help="Overwrite temporal Zarr store if present.")
    ] = False,
):
    if len(sys.argv) < 2:
        raise RuntimeError("Not enough arguments!")

    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    local_store_path = workdir / "volsegtools_workdir"
    if overwrite_tmp and local_store_path.exists():
        shutil.rmtree(local_store_path)

    map_converter = vst.MRCConverter()
    builder = vst.create_builder()
    (
        builder.add_volume_converter(map_converter)
        .add_segmentation_converter(map_converter)
        .set_downsampling_strategy(vst.HierarchyDownsamplingStrategy())
        .set_serializer(vst.MRCSerializer())
        .set_output_dir(local_store_path)
        .set_work_dir(local_store_path)
    )

    try:
        pipeline: vst.ProcessingPipeline = builder.build()
        pipeline.sync_process(
            volumes=volume_source,
            segmentations=segmentation_source,
        )
    finally:
        if rm_tmp and local_store_path.exists():
            shutil.rmtree(local_store_path)


if __name__ == "__main__":
    app()
