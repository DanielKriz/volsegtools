import math

from volsegtools._core.bytes import Bytes
from volsegtools._storage.channel import Channel


def calculate_approx_downsampled_sizes(
    channel: Channel | int, threshold: int, factor: int = 3
) -> list[float]:
    nbytes = channel.handle.nbytes if isinstance(channel, Channel) else channel

    sizes = []
    while nbytes > threshold:
        nbytes /= 2**factor
        if nbytes < threshold:
            break
        sizes.append(nbytes)
    return sizes


def calculate_dimensions(
    channel: Channel | tuple[int, ...], factor: int = 2
) -> list[tuple[int, ...]]:

    def is_valid(shape):
        return all(x > 0 for x in shape)

    shape = channel.handle.shape if isinstance(channel, Channel) else channel

    dimensions = []
    while True:
        shape = tuple(x // factor for x in shape)
        if is_valid(shape):
            dimensions.append(shape)
        else:
            break
    return dimensions


def calculate_steps(channel: Channel | int, threhold: int, factor: int = 2) -> int:
    nbytes = channel.handle.nbytes if isinstance(channel, Channel) else channel
    return len(calculate_approx_downsampled_sizes(nbytes, threhold, factor))


def calculate_min_size_from_resolutions(
    channel: Channel | int, resolution_cnt: int, factor: int = 2
) -> Bytes:
    nbytes = channel.handle.nbytes if isinstance(channel, Channel) else channel

    min_size = nbytes
    for _ in range(resolution_cnt):
        nbytes /= 2**factor
        nbytes = int(nbytes)
        if math.isclose(nbytes, 0):
            break
        min_size = nbytes
    return Bytes(min_size)
