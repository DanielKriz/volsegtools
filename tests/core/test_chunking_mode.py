import volsegtools as vst


def test_chunking_mode_attrs():
    mode = vst.ChunkingMode
    assert hasattr(mode, "AUTO")
    assert hasattr(mode, "NONE")
    assert hasattr(mode, "CUSTOM")
