# VolSeg Tools

A library used for processing of volumes and segmentations.

## Instalation

If you cannot, or don't want to use the [PyPi Package](https://pypi.org/project/volsegtools/), you can install the project locally using [uv](https://docs.astral.sh/uv/):

```
    git clone https://github.com/DanielKriz/volseg-tools
    cd volseg-tools
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

If you wish to be more informed about the processing you might add `--verbose`
option.


Given that we have downloaded some volumetric data, e.g.
[EMD-53130](https://www.ebi.ac.uk/emdb/EMD-53130), we can start the processing
with some downsampling method:

```
molstar-preprocessor --vs EMD-53130.map --strategy tricubic --bundle mvsx --output-path out
```

This is going to create downsampled version of the provided dataset in directory
`out/` in the MVSX archive.

After this step it is possible to drop this archive into, e.g. [Mol*
Viewer](https://molstar.org/viewer/) for visualization.

To get the list of supported downsampling method you can run
`--list-strategies`.

Current implementation is sensitive to the contents of the working directory.
You might want to run `--overwrite-tmp` to ignore the data already stored in the
working directory and run the processing again (effectively overwriting the
contents of the working directory).

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
