import PyQt6 as pyqt
import PyQt6.uic
import PyQt6.QtWidgets as widgets
import sys
import dataclasses
from pathlib import Path
import logging
import enum

import volsegtools as vst

from PySide6.QtCore import QObject, Signal

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QComboBox,
    QPlainTextEdit,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QLineEdit,
    QLabel,
)

import PyQt6.QtGui
from PyQt6.QtGui import QFontDatabase

vst_logger = vst.logger
gui_logger = logging.getLogger("volsegtools_gui")


@dataclasses.dataclass
class PipelineParameters():
    input_kind: vst.DataKind = vst.DataKind.VOLUME
    input_file_path: Path = Path()
    output_dir_path: Path = Path()


class MultiValueStrEnum(str, enum.Enum):
    def __new__(cls, value, *aliases):
        self = str.__new__(cls, value)
        self._value_ = value
        self._aliases_ = aliases
        return self
    
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if value in member._aliases_:
                return member
        return None


class InputKind(MultiValueStrEnum):
    BCIF = "bcif"
    MRC = "mrc", "map", "ccp4"
    IMS = "ims"
    TIFF = "tif", "ome.tif", "tiff", "ome.tiff"
    OBJ = "obj"
    PLY = "ply"
    STL = "stl"
    SFF = "sff"


class GuiLogEmitter(QObject):
    message = Signal(str)


class GuiLogHandler(logging.Handler):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record):
        self.emitter.message.emit(self.format(record))


def is_file_valid() -> bool:
    return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        pyqt.uic.loadUi("vst.ui", self)

        # ---------------------------------------------------------------------
        # State variables for the pipeline
        # ---------------------------------------------------------------------
        self.pipeline_params = PipelineParameters()

        # ---------------------------------------------------------------------
        # Select relevant widgets that will be affected during runtime
        # ---------------------------------------------------------------------

        self.input_kind_select = self.findChild(QComboBox, "input_type_select")

        self.mesh_method_options = self.findChild(QWidget, "mesh_method_options")
        self.mask_method_options = self.findChild(QWidget, "mask_method_options")
        self.volume_method_options = self.findChild(QWidget, "volume_method_options")

        self.mesh_output_group = self.findChild(QWidget, "mesh_output_format_option")
        self.volume_output_group = self.findChild(QWidget, "volume_output_format_option")

        self.logs_space = self.findChild(QPlainTextEdit, "logs_space")
        mono_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        mono_font.setPointSize(8)
        self.logs_space.setFont(mono_font)

        self.begin_processing_button = self.findChild(QPushButton, "begin_processing_button")
        self.cancel_processing_button = self.findChild(QPushButton, "cancel_processing_button")

        self.browse_input_files_button = self.findChild(QPushButton, "input_browse_button")
        self.input_path_edit = self.findChild(QLineEdit, "input_path_edit")
        self.input_format_info = self.findChild(QLabel, "input_format_name_label")

        self.browse_output_dir_button = self.findChild(QPushButton, "output_browse_button")
        self.output_path_edit = self.findChild(QLineEdit, "output_path_edit")

        self.progress_bar = self.findChild(QProgressBar, "progress_bar")


        # ---------------------------------------------------------------------
        # Connect widgets between each other
        # ---------------------------------------------------------------------

        self.input_kind_select.currentTextChanged.connect(self.on_input_kind_select)
        self.begin_processing_button.clicked.connect(self.on_begin_processing)
        self.cancel_processing_button.clicked.connect(self.on_cancel_processing)

        self.browse_input_files_button.clicked.connect(self.on_browse_input_file)
        self.input_path_edit.textChanged.connect(self.update_input_path)
        self.input_path_edit.textChanged.connect(self.update_file_type_guess)

        self.browse_output_dir_button.clicked.connect(self.on_browse_output_dir)
        self.output_path_edit.textChanged.connect(self.update_output_path)

        # ---------------------------------------------------------------------
        # Hide parts that are not important at the start
        # ---------------------------------------------------------------------

        self.mesh_output_group.hide()
        self.mesh_method_options.hide()
        self.mask_method_options.hide()

        # After we have hidden several widgets we want to adjust the size of
        # the window. This way there are not going to be huge ugly gaps.
        self.adjustSize()
        logging.getLogger("volsegtools").info("Application Started")

    def on_input_kind_select(self, text):
        gui_logger.info(f"New selection: {text}")
        match text:
            case "Volume" | "Segmentation Volume":
                self.volume_method_options.show()
                self.volume_output_group.show()
                self.mesh_output_group.hide()
                self.mesh_method_options.hide()
                self.mask_method_options.hide()
            case "Segmentation Mesh":
                self.volume_method_options.hide()
                self.volume_output_group.hide()
                self.mesh_output_group.show()
                self.mesh_method_options.show()
                self.mask_method_options.hide()
            case "Segmentation Mask":
                self.volume_method_options.hide()
                self.volume_output_group.show()
                self.mesh_output_group.hide()
                self.mesh_method_options.hide()
                self.mask_method_options.show()
        # TODO: Find better approach to this later...
        self.adjustSize()

    def append_log_record(self, message: str) -> None:
        self.logs_space.appendPlainText(message)


    def on_begin_processing(self):
        logging.getLogger("volsegtools").info("Started Processing")

    def on_cancel_processing(self):
        logging.getLogger("volsegtools").info("Cancelled Processing")

    def update_file_type_guess(self, new_path) -> None:
        path = Path(str.lstrip(new_path, "."))
        suffix = str.lstrip(path.suffix, ".")
        try:
            self.input_format_info.setText(str(InputKind(suffix).name))
        except:
            self.input_format_info.setText("Unknown")


    def update_input_path(self, new_path) -> None:
        if len(new_path) == 0:
            self.input_path_edit.setStyleSheet("")
            return

        path = Path(new_path)
        if not path.exists():
            self.input_path_edit.setStyleSheet(
                "QLineEdit { background-color: #ffe6e6; }"
            )
            self.input_path_edit.setToolTip("The file does not exists.")
        elif path.is_dir():
            self.input_path_edit.setStyleSheet(
                "QLineEdit { background-color: #ffe6e6; }"
            )
            self.input_path_edit.setToolTip("Points to a directory.")
        else:
            self.input_path_edit.setStyleSheet(
                "QLineEdit { background-color: #dcffd1; }"
            )

        self.pipeline_params.input_file_path = path

    def update_output_path(self, new_path) -> None:
        if len(new_path) == 0:
            self.input_path_edit.setStyleSheet("")
            return

        path = Path(new_path)
        if not path.exists():
            self.output_path_edit.setStyleSheet(
                "QLineEdit { background-color: #ffe6e6; }"
            )
            self.output_path_edit.setToolTip("The file does not exists.")
        elif not path.is_dir():
            self.output_path_edit.setStyleSheet(
                "QLineEdit { background-color: #ffe6e6; }"
            )
            self.output_path_edit.setToolTip("Does not point to a directory.")
        else:
            self.input_path_edit.setStyleSheet(
                "QLineEdit { background-color: #dcffd1; }"
            )

        self.pipeline_params.output_dir_path = path


    def on_browse_output_dir(self):
        print("FSAJDKSADJKSADASK")
        gui_logger.info("Getting an output directory")
        filename = QFileDialog.getExistingDirectory(
            self,
            "Select output directory",
            "",
            # QFileDialog.ShowDirsOnly,
        )

        gui_logger.info(f"As output directory '{filename}' was chosen")
        print(filename)
        if filename:
            self.output_path_edit.setText(filename)

    def on_browse_input_file(self):
        filename, something = QFileDialog.getOpenFileName(
            self,
            "Select input file",
        )
        print(filename)
        print(something)
        if filename:
            self.input_path_edit.setText(filename)


def app():
    app = widgets.QApplication(sys.argv)
    window = MainWindow()

    log_emitter = GuiLogEmitter()
    log_emitter.message.connect(window.append_log_record)
    log_handler = GuiLogHandler(log_emitter)
    log_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    )

    vst_logger.addHandler(log_handler)
    vst_logger.setLevel(level=logging.INFO)
    
    # TODO: add handler for GUI too
    gui_logger.setLevel(level=logging.INFO)

    print(InputKind("mrc"))
    print(InputKind("map"))

    window.show()
    sys.exit(app.exec())
