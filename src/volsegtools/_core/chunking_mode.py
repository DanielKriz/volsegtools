import enum


class ChunkingMode(enum.Enum):
    """Chunking mode enumeration."""

    AUTO = 1
    NONE = 2
    CUSTOM = 3
