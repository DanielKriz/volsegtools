import warnings

from volsegtools.abc.converter import Converter


class UnsupportedCompressionError(Exception):
    def __init__(self):
        super().__init__("Unsupported compression for this file type")


class ConverterMap:
    def __init__(self) -> None:
        self._suffix_to_converter_map: dict[str, Converter] = {}

    def set_converter(
        self,
        converter,
        suffixes: list[str] | str | None = None,
        force=False,
    ) -> None:
        for suffix in self.split_suffixes(suffixes):
            if suffix in self._suffix_to_converter_map and not force:
                warnings.warn(
                    f"Overwriting converter for suffix: {suffix}",
                    RuntimeWarning,
                    stacklevel=2,
                )
            self._suffix_to_converter_map[suffix] = converter

            if converter.supports_compression:
                self._suffix_to_converter_map[suffix + ".gz"] = converter
                self._suffix_to_converter_map[suffix + ".bz2"] = converter

        if not suffixes:
            self.set_converter(converter, converter.supported_suffixes)

    def is_empty(self) -> bool:
        return len(self._suffix_to_converter_map.values()) == 0

    def split_suffixes(self, suffixes):
        if isinstance(suffixes, str):
            return suffixes.split("|")
        return suffixes

    def get_converter(self, suffix) -> Converter:
        # we are graceful for suffixes that start with a dot.
        suffix = suffix.strip(".")
        try:
            return self._suffix_to_converter_map[suffix]
        except KeyError:
            if suffix.endswith(("gz", "bz2")):
                raise UnsupportedCompressionError() from None
            raise

    def __getitem__(self, suffix) -> Converter:
        return self.get_converter(suffix)

    def __str__(self):
        return str(self._suffix_to_converter_map)
