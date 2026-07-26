from typing import Optional, List, Callable, Any
import pydantic
import enum
import dataclasses

from volsegtools._core.timer import Timer
from volsegtools._core.working_store import WorkingStore

class PipelineStageKind(enum.StrEnum):
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
class PipelineState():
    current_stage: PipelineStageKind
    msg: Optional[str]


class PipelineStateManager:
    def __init__(
        self,
        pipeline: "ProcessingPipeline",
        initial_state: PipelineState,
    ) -> None:
        self._pipeline = pipeline
        self._state = initial_state
        self._callbacks: List[Callable] = []

    @property
    def current(self) -> PipelineState:
        return self._state

    def add_callback(self, cb: Callable):
        self._callbacks.append(cb)

    def update(self, **kwargs: Any) -> None:
        self._state = dataclasses.replace(self._state, *kwargs)
        for cb in self._callbacks:
            cb(self.current)

@dataclasses.dataclass()
class PipelineContext:
    timer: Timer
    working_store: WorkingStore
    state: PipelineStateManager
