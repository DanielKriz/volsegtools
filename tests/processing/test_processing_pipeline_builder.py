from pathlib import Path

import itertools

import pytest

import volsegtools as vst


class MockConverter(vst.abc.Converter):
    async def convert_volume(self, input_path, context):
        return []

    async def convert_segmentation(self, input_path, context):
        return []

    async def collect_metadata(self, input_path, context):
        return []

    async def collect_annotations(self, input_path, context):
        return []


class MockSerializer(vst.abc.Serializer):
    async def serialize(self, data_set, output_path, context):
        return []


def generate_data_kind_permutations():
    data_kinds = [
        vst.DataKind.VOLUME,
        vst.DataKind.SEGMENTATION_MASK,
        vst.DataKind.SEGMENTATION_MESH,
        vst.DataKind.SEGMENTATION_VOLUME,
    ]

    results = []
    results += itertools.combinations(data_kinds, 1)
    results += itertools.combinations(data_kinds, 2)
    results += itertools.combinations(data_kinds, 3)
    results += itertools.combinations(data_kinds, 4)
    return results


@pytest.mark.parametrize(
    "data_kinds",
    [*generate_data_kind_permutations()],
    ids=lambda x: f"data_kinds={x}",
)
def test_valid_construction_with_serializer(data_kinds):
    builder = vst.ProcessingPipelineBuilder()
    for kind in data_kinds:
        builder.set_serializer(kind, MockSerializer())
    builder.set_work_dir(Path("unused"))

    builder.build()
