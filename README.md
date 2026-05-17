# VolSeg Tools

A library used for processing of volumes and segmentations.

## Instalation

If you cannot, or don't want to use the [PyPi Package](https://pypi.org/project/volsegtools/), you can install the project locally using [uv](https://docs.astral.sh/uv/):

```
    git clone https://github.com/DanielKriz/volseg-tools
    cd volseg-tools
    uv init
    uv venv
    source .venv/bin/activate
    uv pip install .
```

## Usage

The library is intended for definition of processing pipelines for volumetric
data and segmentations.

Next to that a CLI preprocessing application is provided. After the installation
you can run:

```
molstar-preprocessor --help
```
## Support

### Input Formats

- MRC
- NiBabel
- SFF
- Imaris Bitplane
- STL, OBJ, PLY
- VRML
- OME-TIFF
- OME-NGFF

### Serialization Formats

- MRC
- BCIF

### Bundling Formats

- MVSX
- Zip per resolution
- Zip

## License

This project is licensed under the **MIT**. See the [LICENSE](LICENSE) for more
information.
