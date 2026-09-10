from volsegtools._storage.channel import Channel
from volsegtools._core.bytes import Bytes
import math


def calculate_approx_downsampled_sizes(
    channel: Channel | int, size_threshold: int, factor: int = 3
) -> list[float]:
    if isinstance(channel, Channel):
        bytes_count = channel.handle.nbytes
    else:
        bytes_count = channel

    sizes = []
    while bytes_count > size_threshold:
        bytes_count /= 2**factor
        if bytes_count < size_threshold:
            break
        sizes.append(bytes_count)
    return sizes


def calculate_steps(channel: Channel | int, size_threhold: int, factor: int = 2) -> int:
    if isinstance(channel, Channel):
        bytes_count = channel.handle.nbytes
    else:
        bytes_count = channel

    return len(calculate_approx_downsampled_sizes(bytes_count, size_threhold, factor))

def calculate_min_size_from_resolutions(
    channel: Channel | int,
    resolution_cnt: int,
    factor: int = 2
) -> Bytes:
    if isinstance(channel, Channel):
        bytes_count = channel.handle.nbytes
    else:
        bytes_count = channel

    min_size = bytes_count
    for _ in range(resolution_cnt):
        bytes_count /= 2**factor
        bytes_count = int(bytes_count)
        if math.isclose(bytes_count, 0):
            break
        min_size = bytes_count
    return Bytes(min_size)
