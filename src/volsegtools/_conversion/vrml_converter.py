from pathlib import Path
from typing import ClassVar

import json
import tempfile

import vrmlxpy as vrml

from volsegtools._conversion.mesh_converter import MeshConverter
from volsegtools._model import PipelineContext
from volsegtools._storage import DataSet
from volsegtools.abc import Converter


class VRMLConverter(Converter):
    DEFAULT_CONFIG: ClassVar[dict] = {
        "ignoreUnknownNode": False,
        "logFileName": "vrmlproc",
        "logFileDirectory": ".",
        "synonymsFile": "./synonymsFile.json",
        "exportFormat": {"format": "stl", "options": {"binary": True}},
        "parallelismSettings": {"active": True, "threadsNumberLimit": 4},
        "meshSimplification": {"active": False, "percentageOfAllEdgesToSimplify": 50},
        "IFSSettings": {"checkRange": True},
    }

    DEFAULT_SYNONYMS: ClassVar[dict[str, str]] = {
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

    async def convert_volume(self, input_path: Path, context) -> list[DataSet]:
        raise RuntimeError("This converter does not support volumes!")

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        with (
            tempfile.NamedTemporaryFile() as tmp_config,
            tempfile.NamedTemporaryFile() as tmp_synonyms,
            tempfile.NamedTemporaryFile(suffix=".stl") as tmp_out,
        ):
            config = self.DEFAULT_CONFIG.copy()
            config["synonymsFile"] = str(tmp_synonyms.name)

            with Path.open(Path(tmp_config.name), "w") as file:
                file.write(json.dumps(config))
            with Path.open(Path(tmp_synonyms.name), mode="w") as file:
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
