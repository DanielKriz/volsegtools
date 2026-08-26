import volsegtools as vst


def test_descriptive_statistics_construction():
    stats = vst.DescriptiveStatistics(0.0, 0.0, 0.0, 0.0)
    assert hasattr(stats, "mean")
    assert hasattr(stats, "std")
    assert hasattr(stats, "max")
    assert hasattr(stats, "min")


def test_dataset_info_construction():
    dataset_info = vst.DataSetInfo()
    assert hasattr(dataset_info, "filename")
    assert hasattr(dataset_info, "resolution")
    assert hasattr(dataset_info, "axis_order")
    assert hasattr(dataset_info, "cell_size")
    assert hasattr(dataset_info, "origin")
    assert hasattr(dataset_info, "id")
    assert hasattr(dataset_info, "kind")
    assert hasattr(dataset_info, "lattice_shape")


def test_time_frame_info_construction():
    frame_info = vst.TimeFrameInfo()
    assert hasattr(frame_info, "id")


def test_channel_info_struction():
    channel_info = vst.ChannelInfo()
    assert hasattr(channel_info, "id")
    assert hasattr(channel_info, "statistics")


def test_mesh_info_struction():
    mesh_info = vst.MeshInfo()
    assert hasattr(mesh_info, "id")
