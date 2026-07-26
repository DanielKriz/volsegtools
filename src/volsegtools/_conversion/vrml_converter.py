import json
import tempfile
from pathlib import Path

import vrmlxpy as vrml

from volsegtools._conversion.mesh_converter import MeshConverter
from volsegtools._model import PipelineContext
from volsegtools._storage import DataSet
from volsegtools.abc import Converter


class VRMLConverter(Converter):
    DEFAULT_CONFIG = {
        "ignoreUnknownNode": False,
        "logFileName": "vrmlproc",
        "logFileDirectory": ".",
        "synonymsFile": "./synonymsFile.json",
        "exportFormat": {"format": "stl", "options": {"binary": True}},
        "parallelismSettings": {"active": True, "threadsNumberLimit": 4},
        "meshSimplification": {"active": False, "percentageOfAllEdgesToSimplify": 50},
        "IFSSettings": {"checkRange": True},
    }

    DEFAULT_SYNONYMS = {
        "VRMLGroup": "Group",
        "VRMLTransform": "Transform",
        "VRMLSwitch": "Switch",
        "VRMLIndexedFaceSet": "IndexedFaceSet",
        "VRMLIndexedLineSet": "IndexedLineSet",
        "VRMLBox": "Box",
        "VRMLShape": "Shape",
        "VRMLColor": "Color",
        "VRMLCoordinate": "Coordinate",
        "VRMLNormal": "Normal",
        "VRMLTextureCoordinate": "TextureCoordinate",
        "VRMLAppearance": "Appearance",
        "VRMLWorldInfo": "WorldInfo",
        "VRMLMaterial": "Material",
        "VRMLImageTexture": "ImageTexture",
        "VRMLPixelTexture": "PixelTexture",
        "VRMLTextureTransform": "TextureTransform",
        "VRMLCone": "Cone",
        "VRMLCylinder": "Cylinder",
        "VRMLElevationGrid": "ElevationGrid",
        "VRMLExtrusion": "Extrusion",
        "VRMLPointSet": "PointSet",
        "VRMLSphere": "Sphere",
        "VRMLText": "Text",
        "VRMLAnchor": "Anchor",
        "VRMLBillboard": "Billboard",
        "VRMLCollision": "Collision",
        "VRMLInline": "Inline",
        "VRMLLOD": "LOD",
        "VRMLFontStyle": "FontStyle",
    }

    @property
    def supported_suffixes(self):
        return ["wrl", "vrml"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path, context) -> list[DataSet]:
        raise RuntimeError("This converter does not support volumes!")

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        tmp_config = tempfile.NamedTemporaryFile()
        tmp_synonyms = tempfile.NamedTemporaryFile()
        tmp_out = tempfile.NamedTemporaryFile(suffix=".stl")

        config = self.DEFAULT_CONFIG.copy()
        config["synonymsFile"] = str(tmp_synonyms.name)

        with open(str(tmp_config.name), "w") as file:
            file.write(json.dumps(config))
        with open(str(tmp_synonyms.name), "w") as file:
            file.write(json.dumps(self.DEFAULT_SYNONYMS))

        vrml.convert_vrml(
            str(input_path),
            str(tmp_out.name),
            str(tmp_config.name),
        )

        mesh_converter = MeshConverter()
        return await mesh_converter.convert_segmentation(Path(tmp_out.name))

    async def collect_annotations(self, input_path, context) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError
