from collections.abc import Callable
from pathlib import Path
from typing import Any

import dataclasses
import enum

import pydantic

from volsegtools._core import Bytes, Timer, WorkingStore


class PipelineStageKind(enum.StrEnum):
    """Representation of the current state of the pipeline."""

    NOT_STARTED = "Not Started"
    CONVERTING_VOLUMES = "Volume Conversion"
    CONVERTING_SEGMENTATIONS = "Segmentation Conversion"
    COLLECTING_METADATA = "Metadata Collection"
    COLLECTING_ANNOTATIONS = "Annotation Collection"
    POST_CONVERT = "Post-Conversion Steps"
    DOWNSAMPLING = "Downsampling"
    POST_PROCESS = "Post-Processing Steps"
    SERIALIZATION = "Serialization"
    BUNDLING = "Bundling"
    FINISHED = "Finished"
    CUSTOM = enum.auto()


@pydantic.dataclasses.dataclass()
class PipelineState:
    """Dataclass for holding the pipeline's state.

    Attributes
    ----------
    stage: PipelineStageKind
        Current stage of the pipeline.
    msg: str, optional
        Optional message associated with the current stage.
    """

    stage: PipelineStageKind
    msg: str | None


class PipelineStateManager:
    """Manager of the pipeline state.

    It is responsible for calling callbacks on change and for current state
    management.
    """

    def __init__(
        self,
        pipeline,
        initial_state: PipelineState,
    ) -> None:
        """
        Parameters
        ----------
        pipeline: ProcessingPipeline
            The pipeline with which should this manager be associated.
        initial_state: PipelineState
            The initial state of the manager.
        """
        self._pipeline = pipeline
        self._state = initial_state
        self._callbacks: list[Callable] = []

    @property
    def current(self) -> PipelineState:
        """Returns the current state of the whole pipeline.

        Returns
        -------
        PipelineState:
            Current state of the pipeline.
        """
        return self._state

    def add_callback(self, cb: Callable) -> None:
        """Add new callback that shall be called on each state change.

        Parameters
        ----------
        cb: Callable
            New callback.
        """
        self._callbacks.append(cb)

    def update(self, **kwargs: Any) -> None:
        """Updates the pipeline state.

        On each call of this method all callbacks are called.

        Parameters
        ----------
        kwargs: Any
            Key-Value pairs that should be updated in the pipeline's state.
        """
        self._state = dataclasses.replace(self._state, **kwargs)
        for cb in self._callbacks:
            cb(self.current)


@dataclasses.dataclass()
class PipelineContext:
    """Context of the pipeline that should be accessible in each stage.

    It is required to make runs of different pipeline's independent.

    Attributes
    ----------
    timer: Timer
        Pipeline's timer.
    working_store: WorkingStore
        Current working store.
    output_dir: Path
        Output directory associated with this pipeline.
    state: PipelineStateManager
        Current pipeline state manager.
    size_threhold: Bytes
        Size threshold that is accepted by this pipeline.
    """

    timer: Timer
    working_store: WorkingStore
    output_dir: Path
    state: PipelineStateManager
    size_threshold: Bytes
