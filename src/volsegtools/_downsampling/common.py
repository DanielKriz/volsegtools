from volsegtools._storage.channel import Channel

def calculate_approx_downsampled_sizes(
    channel: Channel,
    size_threshold: int,
    factor: int = 3
) -> list[float]:
    bytes_count = channel.handle.nbytes
    sizes = []
    while bytes_count > size_threshold:
        bytes_count /= 2**factor
        if bytes_count < size_threshold:
            break
        sizes.append(bytes_count)
    return sizes

def calculate_steps(channel: Channel, size_threhold: int) -> int:
    return len(calculate_approx_downsampled_sizes(channel, size_threhold))

