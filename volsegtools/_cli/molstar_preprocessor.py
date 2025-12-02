import os
import sys
import typer
import shutil
import logging

from pathlib import Path
from typing import List
from typing_extensions import Annotated

from volsegtools.converter import MapConverter
from volsegtools.preprocessor import (
    PreprocessorBuilder,
    Preprocessor,
)
# TODO: parameters should (and can be) moved to the downsampler package
from volsegtools.downsampler import (
    HierarchyDownsampler, 
)
from volsegtools.core import (
    DownsamplingParameters,
)


app = typer.Typer()


@app.command()
def run(
    volume_source: Annotated[List[Path], typer.Option(
        help="Specifies a path to volumetric data."
    )] = [],
    segmentation_source: Annotated[List[Path], typer.Option(
        help="Specifies a path to segmentation data."
    )] = [],
    workdir: Annotated[Path, typer.Option(
        help="Remove temporal Zarr store created during downsampling."
    )] = Path.cwd(),
    rm_tmp: Annotated[bool, typer.Option(
        help="Remove temporal Zarr store created during downsampling."
    )] = False,
    overwrite_tmp: Annotated[bool, typer.Option(
        help="Overwrite temporal Zarr store if present."
    )] = False,
):
    if len(sys.argv) < 2:
        raise RuntimeError('Not enough arguments!')

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    local_store_path = workdir / "volsegtools_tmp"
    if overwrite_tmp and local_store_path.exists():
        shutil.rmtree(local_store_path)

    builder = PreprocessorBuilder()
    builder.set_converter(MapConverter())
    builder.set_downsampler(HierarchyDownsampler())

    for file in volume_source:
        logging.debug(f"Adding file: '{file}' as a volume source.")
        builder.add_volume_src_file(file)

    for file in segmentation_source:
        logging.debug(f"Adding file: '{file}' as a segmentation source.")
        builder.add_segmentation_src_file(file)

    builder.set_output_dir(local_store_path)

    try:
        preprocessor: Preprocessor = builder.build()
        preprocessor.sync_preprocess()
        preprocessor.serialize()
    finally:
        if rm_tmp and local_store_path.exists():
            shutil.rmtree(local_store_path)


if __name__ == '__main__':
    app()

