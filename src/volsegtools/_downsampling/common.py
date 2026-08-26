from volsegtools._storage.channel import Channel


def calculate_approx_downsampled_sizes(
    channel: Channel, size_threshold: int, factor: int = 2
) -> list[float]:
    """Calculates approximate downsampling sizes.

    Parameters
    ----------
    channel: Channel
        The source of the original resolution.
    size_threshold: int
        The minimal size for a resolution to be accepted.
    factor: int
        A single dimension of the downsampling kernel. So factor equal to 2
        would result into 1/8th of the size of the previous resolution.

    Returns
    -------
    list[float]:
        List of approximate downsampled sizes of different resolutions.
    """
    if factor <= 1:
        raise RuntimeError("Factor <= 1 wouldn't lead to downsampling")

    if size_threshold <= 0:
        raise RuntimeError("Size threshold has to be bigger than zero")

    bytes_count = channel.handle.nbytes
    sizes = []
    while bytes_count > size_threshold:
        bytes_count /= factor**3
        if bytes_count < size_threshold:
            break
        sizes.append(bytes_count)
    return sizes


def calculate_steps(channel: Channel, size_threhold: int, factor: int = 2) -> int:
    """Calculates the number of downsampling steps.

    See: calculate_approx_downsampled_sizes for more info about parameters.

    Returns
    -------
    int:
        Number of downsampling steps.
    """
    return len(calculate_approx_downsampled_sizes(channel, size_threhold, factor))
