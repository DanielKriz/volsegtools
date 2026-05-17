import logging
import shutil
from pathlib import Path
from typing import List
import enum
import rich
import rich.console
import rich.logging
import itertools

import typer
from typing_extensions import Annotated

import volsegtools as vst
from volsegtools._core.data_kind import DataKind

vst_logger = logging.getLogger("volsegtools")

app = typer.Typer()


class DownsamplignAlgorithmKind(enum.StrEnum):
    NEAREST_NEIGHBOR = "nearest"
    MAX = "max"
    MIN = "min"
    AVG = "avg"
    TRILINEAR = "trilinear"
    TRICUBIC = "tricubic"
    TRIQUINTIC = "triquintic"
    TRIQUINTIC_NO_SMOOTH = "triquintic_no_smooth"
    SMOOTHING = "smoothing"
    STRIDED_SMOOTHING = "strided_smoothing"
    SEPARATED_SMOOTHING = "separated_smoothing"
    NULL = "null"


class ErrorFunctionKind(enum.StrEnum):
    MSE = "mse"
    MAE = "mae"
    RMSE = "rmse"
    PSNR = "psnr"
    SSIM = "ssim"
    VFM = "vfm"
    HFEN = "hfen"


class BundlingKind(enum.StrEnum):
    NULL = "null"
    MVXS = "mvsx"
    RESOLUTION_ZIP = "resolution_zip"
    ZIP = "zip"


class SerializerKind(enum.StrEnum):
    BCIF = "bcif"
    MRC = "mrc"
    OBJ = "obj"
    PLY = "ply"
    STL = "stl"


def get_serializer(kind: SerializerKind):
    match kind:
        case SerializerKind.BCIF:
            return vst.BCIFSerializer()
        case SerializerKind.MRC:
            return vst.MRCSerializer()
        case SerializerKind.OBJ:
            return vst.OBJSerializer()
        case SerializerKind.PLY:
            return vst.PLYSerializer()
        case SerializerKind.STL:
            return vst.STLSerializer()
        case _:
            raise RuntimeError("Unknown kind encountered")


def get_downsampling_strategy(kind: DownsamplignAlgorithmKind):
    match kind:
        case DownsamplignAlgorithmKind.NEAREST_NEIGHBOR:
            return vst.NearestNeighborDownsamplingStrategy()
        case DownsamplignAlgorithmKind.MAX:
            return vst.MaxPoolingStrategy()
        case DownsamplignAlgorithmKind.MIN:
            return vst.MinPoolingStrategy()
        case DownsamplignAlgorithmKind.AVG:
            return vst.AveragePoolingStrategy()
        case DownsamplignAlgorithmKind.TRILINEAR:
            return vst.TrilinearInterpolation()
        case DownsamplignAlgorithmKind.TRICUBIC:
            return vst.TricubicInterpolation()
        case DownsamplignAlgorithmKind.TRIQUINTIC:
            return vst.TriquinticInterpolation()
        case DownsamplignAlgorithmKind.TRIQUINTIC_NO_SMOOTH:
            return vst.TriquinticInterpolation()
        case DownsamplignAlgorithmKind.SMOOTHING:
            return vst.HierarchyDownsamplingStrategy()
        case DownsamplignAlgorithmKind.STRIDED_SMOOTHING:
            return vst.StridedSmoothing(vst.Gaussian3DKernel(5, 1))
        case DownsamplignAlgorithmKind.SEPARATED_SMOOTHING:
            return vst.SeparableSmoothing(5, 1)
        case DownsamplignAlgorithmKind.NULL:
            return vst.NullDownsamplingStrategy()
        case _:
            return vst.NullDownsamplingStrategy()


class CommandGroup(enum.StrEnum):
    DEFAULT = "Default"
    BENCHMARK_AND_DEBUG = "Benchmarking & Debugging"


@app.command()
def run(
    volume_source: Annotated[
        List[Path],
        typer.Option(
            "--volume-source",
            "--vs",
            help="Specifies a path to volumetric data.",
        ),
    ] = [],
    segmentation_source: Annotated[
        List[Path],
        typer.Option(
            "--segmentation-source",
            "--ss",
            help="Specifies a path to segmentation data.",
        ),
    ] = [],
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            help="Verbose logging.",
            rich_help_panel=CommandGroup.BENCHMARK_AND_DEBUG,
            count=True,
        ),
    ] = 0,
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
    error_func: Annotated[
        List[ErrorFunctionKind] | None,
        typer.Option(
            help="Which error functions shall be used for evaluation",
            rich_help_panel=CommandGroup.BENCHMARK_AND_DEBUG,
            case_sensitive=False,
        ),
    ] = None,
    eval_size: Annotated[
        bool,
        typer.Option(
            help="Report size measurements",
            rich_help_panel=CommandGroup.BENCHMARK_AND_DEBUG,
        ),
    ] = False,
    size_report_path: Annotated[
        Path | None,
        typer.Option(
            help="Where should we store size report",
            rich_help_panel=CommandGroup.BENCHMARK_AND_DEBUG,
        ),
    ] = None,
    show_time: Annotated[
        bool,
        typer.Option(
            help="Report time measurements",
            rich_help_panel=CommandGroup.BENCHMARK_AND_DEBUG,
        ),
    ] = False,
    time_report_path: Annotated[
        Path | None,
        typer.Option(
            help="Where should we store time report",
            rich_help_panel=CommandGroup.BENCHMARK_AND_DEBUG,
        ),
    ] = None,
    strategy: Annotated[
        DownsamplignAlgorithmKind,
        typer.Option(
            help="Name of downsampling strategy",
            metavar="METHOD",
            case_sensitive=False,
        ),
    ] = DownsamplignAlgorithmKind.NULL,
    list_strategies: Annotated[
        bool,
        typer.Option(
            help="List available downsampling strategies and exit.",
        ),
    ] = False,
    volume_serializer: Annotated[
        SerializerKind,
        typer.Option(
            help="Serializer for the segmentation meshes.",
            metavar="SERIALIZER",
        ),
    ] = SerializerKind.MRC,
    segmentation_volume_serializer: Annotated[
        SerializerKind,
        typer.Option(
            help="Serializer for the segmentation meshes.",
            metavar="SERIALIZER",
        ),
    ] = SerializerKind.MRC,
    segmentation_mask_serializer: Annotated[
        SerializerKind,
        typer.Option(
            help="Serializer for the segmentation meshes.",
            metavar="SERIALIZER",
        ),
    ] = SerializerKind.MRC,
    segmentation_mesh_serializer: Annotated[
        SerializerKind,
        typer.Option(
            help="Serializer for the segmentation meshes.",
            metavar="SERIALIZER",
        ),
    ] = SerializerKind.PLY,
    bundling_approach: Annotated[
        BundlingKind,
        typer.Option(
            "--bundle",
            "-b",
            help="Type of bundling.",
            case_sensitive=False,
        ),
    ] = BundlingKind.NULL,
):

    # TODO: Add early check here, whether files exist
    for file_path in itertools.chain(volume_source, segmentation_source):
        if not file_path.exists():
            vst_logger.error(f"The file: {file_path} does not exists")
            raise typer.Exit()

    if list_strategies:
        for idx, strategy in enumerate(DownsamplignAlgorithmKind):
            print(f"{idx}: {strategy}")
        raise typer.Exit()

    console = rich.console.Console()

    vst.logger.addHandler(rich.logging.RichHandler(console=console, show_time=False))
    if verbose > 0:
        vst.logger.setLevel(level=logging.INFO)

    local_store_path = workdir / "volsegtools_workdir"
    if overwrite_tmp and local_store_path.exists():
        shutil.rmtree(local_store_path)

    map_converter = vst.MRCConverter()
    builder = vst.create_builder()
    (
        builder.add_volume_converter(map_converter)
        .add_volume_converter(vst.TIFFConverter())
        .add_volume_converter(vst.NGFFConverter())
        .add_volume_converter(vst.ImarisConverter())
        .add_segmentation_converter(vst.MeshConverter())
        .add_segmentation_converter(map_converter)
        .set_downsampling_strategy(get_downsampling_strategy(strategy))
        .set_serializer(DataKind.VOLUME, get_serializer(volume_serializer))
        .set_serializer(
            DataKind.SEGMENTATION_MASK, get_serializer(segmentation_mask_serializer)
        )
        .set_serializer(
            DataKind.SEGMENTATION_VOLUME, get_serializer(segmentation_volume_serializer)
        )
        .set_serializer(
            DataKind.SEGMENTATION_MESH, get_serializer(segmentation_mesh_serializer)
        )
        .set_output_dir(local_store_path)
        .set_work_dir(local_store_path)
    )

    match bundling_approach:
        case BundlingKind.MVXS:
            builder.set_bundler(vst.MVSXBundler())
        case BundlingKind.RESOLUTION_ZIP:
            ...
        case BundlingKind.ZIP:
            ...
    vst_logger.info(f"Setting bundler to: '{bundling_approach}'")

    if strategy == DownsamplignAlgorithmKind.TRIQUINTIC:
        builder.add_post_process_step(vst.SmoothingStep())

    # TODO: make strategy part of data set metadata

    if eval_size:
        if size_report_path is not None:
            reporter = vst.JSONSizeReporter(size_report_path)
        else:
            reporter = vst.StdoutSizeReporter()
        builder.add_post_process_step(
            vst.SizeEvaluationStep(
                reporter,
                label=f"{strategy}",
            )
        )

    if error_func is not None:
        builder.add_post_process_step(
            vst.ErrorEvaluationMultiStep(
                [str(e) for e in error_func],
                output_path=workdir / "errors.json",
                label=f"{strategy}",
            )
        )

    with console.status("Processing..."):
        try:
            pipeline: vst.ProcessingPipeline = builder.build()
            pipeline.sync_process(
                volumes=volume_source,
                segmentations=segmentation_source,
            )

            vst.Timer.pop_stage()
        finally:
            if rm_tmp and local_store_path.exists():
                shutil.rmtree(local_store_path)

    if show_time:
        vst.Timer.print_report(vst.TimerReporter())
    if time_report_path:
        # TODO: this has to be more sophisticated
        vst.Timer.print_report(
            vst.JSONTimerReporter(
                output_path=time_report_path,
                label=volume_source[0].stem,
                method=str(strategy),
            )
        )


if __name__ == "__main__":
    app()
    typer.Exit(code=0)
