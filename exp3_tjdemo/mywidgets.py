import itertools
import math
import sys
from loguru import logger
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QGridLayout,
    QTextEdit,
    QLabel,
    QFileDialog
)


class Gridworld(QtWidgets.QWidget):
    def __init__(self, rows, cols, **kwargs):
        super(Gridworld, self).__init__()

        # Properties
        self._rows = rows
        self._cols = cols
        self._cells = dict()

        # Main layout
        self._main_layout = QGridLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        # Add cells
        for r in range(rows):
            for c in range(cols):
                self._cells[r, c] = Cell(name=f"({r}, {c})", **kwargs)
                self._main_layout.addWidget(self._cells[r, c], r, c)

        # Set main layout
        self.setLayout(self._main_layout)

    def cells(self):
        return self._cells.values()


class Cell(QtWidgets.QWidget):
    def __init__(self, name, **kwargs):
        """
        :param name: (str) Name of the cell.
        :param kwargs: Options
            - parent: (QWidget) Parent widget.
            - backcolor: (str) Color of the cell.
            - widget_capacity: (int) Maximum number of widgets that can be added to the cell.
            - min_width: (int) Minimum width of the cell.
            - min_height: (int) Minimum height of the cell.
            - max_width: (int) Maximum width of the cell.
            - max_height: (int) Maximum height of the cell.
            - show_name: (bool) Whether to show the name of the cell.
            - name_position: (int) Position of the name of the cell.
                Options (case-insensitive): ["N", "E", "S", "W", "NE", "SE", "SW", "NW", "CENTER"]
            - font_size: (int) Font size of the name of the cell.
        """
        super(Cell, self).__init__(parent=kwargs.get("parent", None))

        # Properties (Readonly)
        self._name = name

        # Properties (Read/Write)
        self._backcolor = kwargs.get("color", "white")
        self._widget_capacity = kwargs.get("widget_capacity", 4)
        self._min_width = kwargs.get("min_width", 100)
        self._min_height = kwargs.get("min_height", 100)
        self._max_width = kwargs.get("max_width", 200)
        self._max_height = kwargs.get("max_height", 200)
        self._border_width = kwargs.get("border_width", 2)
        self._border_style = kwargs.get("border_width", "solid")
        self._border_color = kwargs.get("border_color", "black")
        self._show_name = kwargs.get("show_name", 100)
        self._name_position = kwargs.get("name_position", "NW")
        self._font_size = kwargs.get("font_size", 10)
        self._state_is_selected = False
        self.setStyleSheet(
            f"border: {self._border_width}px {self._border_style} {self._border_color}; "
            f"min-width: {self._min_width}px; "
            f"min-height: {self._min_height}px; "
            f"max-width: {self._max_width}px; "
            f"max-height: {self._max_height}px; "
        )

        # Widgets
        self._widgets = dict()

        # Main Layout
        self._main_layout = QtWidgets.QGridLayout()
        self._main_layout.setContentsMargins(15, 15, 15, 15)

        self._main_layout_cols = math.ceil(math.sqrt(self._widget_capacity))
        self._main_layout_rows = math.ceil(self._widget_capacity / self._main_layout_cols)

        # Main canvas
        canvas_cell_name = self._name if self._show_name else ""
        canvas_cell_name_alignment = self._get_name_alignment()
        self._canvas = QLabel(canvas_cell_name, alignment=canvas_cell_name_alignment)
        self._canvas.setStyleSheet(
            f"font-size: {self._font_size}px; "
            f"background-color: {self._backcolor};"
        )
        self._main_layout.addWidget(self._canvas, 0, 0, -1, -1)

        # Set main layout
        self.setLayout(self._main_layout)

    def _get_name_alignment(self):
        if self._name_position.upper() == "N":
            label_text_align = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        elif self._name_position.upper() == "E":
            label_text_align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        elif self._name_position.upper() == "S":
            label_text_align = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        elif self._name_position.upper() == "W":
            label_text_align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif self._name_position.upper() == "NE":
            label_text_align = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        elif self._name_position.upper() == "SE":
            label_text_align = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        elif self._name_position.upper() == "SW":
            label_text_align = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft
        elif self._name_position.upper() == "NW":
            label_text_align = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        else:
            label_text_align = Qt.AlignmentFlag.AlignCenter
        return label_text_align

    def _get_next_available_position(self):
        """
        Logic to determine grid layout and position the tiles.
        Returns the next free cell available to place a new tile.
        """
        if len(self._widgets) == self._widget_capacity:
            return None

        positions = set(itertools.product(range(self._main_layout_rows), range(self._main_layout_cols)))
        return min(positions - set(self._widgets.keys()))

    def add_widget(self, widget):
        pos = self._get_next_available_position()
        if pos is None:
            logger.warning(f"Cell {self._name} is full. Cannot add widget.")
            return

        self._widgets[pos] = widget
        self.update()

    def has_widget(self, name):
        for widget in self._widgets.values():
            if widget.name() == name:
                return True

    def remove_widget(self, name):
        pos = None
        for k, v in self._widgets.items():
            if v.name() == name:
                pos = k
                break
        if pos is not None:
            widget_to_remove = self._main_layout.itemAtPosition(pos[0], pos[1])
            self._main_layout.removeWidget(widget_to_remove.widget())
            self._widgets.pop(pos)
            self._canvas.update()

    def paintEvent(self, e):
        # Add logic to determine size.
        if len(self._widgets) == 0:
            self._canvas.clear()
            return
        for pos, widget in self._widgets.items():
            widget.set_size(30, 30)
            widget.setStyleSheet(
                f"border: {0}px {self._border_style} {self._border_color}; "
                f"min-width: 0px; "
                f"min-height: 0px; "
                f"max-width: {self._max_width}px; "
                f"max-height: {self._max_height}px; "
            )
            self._main_layout.addWidget(widget, pos[0], pos[1])

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._state_is_selected = not self._state_is_selected
        if self._state_is_selected:
            self.setStyleSheet(f"border: 3px solid green; ")
        else:
            self.setStyleSheet(f"border: 2px solid black; ")

    def name(self):
        return self._name


class ImageButton(QPushButton):
    def __init__(self, name, impath, **kwargs):
        super(ImageButton, self).__init__(parent=kwargs.get("parent", None))

        # Properties
        self._name = name
        self._impath = impath

        # Main Layout
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        # Canvas for image drawing
        self._canvas = QLabel()
        # self._canvas.setStyleSheet(
        #     f"min-width: {self.width()}px; "
        #     f"min-height: {self.height()}px; "
        #
        # )
        self._canvas.setScaledContents(True)

        # Draw image
        self._pixmap = QtGui.QPixmap(self._impath)
        self._canvas.setPixmap(self._pixmap)
        self.setStyleSheet(f"border: 1px solid black; ")
        self._main_layout.addWidget(self._canvas)
        self.setLayout(self._main_layout)
        self._state_is_selected = False

    def scale(self, factor):
        pixmap = QtGui.QPixmap(self._impath)
        width, height = pixmap.rect().width(), pixmap.rect().height()
        self._pixmap = pixmap.scaled(int(factor * width), int(factor * height), Qt.AspectRatioMode.KeepAspectRatio)
        self._canvas.setPixmap(self._pixmap)

    def set_size(self, width, height):
        pixmap = QtGui.QPixmap(self._impath)
        self._pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        self._canvas.setPixmap(self._pixmap)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self._state_is_selected = not self._state_is_selected

    def set_selected(self, value):
        self._state_is_selected = value
        if self._state_is_selected:
            self.setStyleSheet(f"border: 3px solid green; ")
        else:
            self.setStyleSheet(f"border: 1px solid black; ")

    def is_selected(self):
        return self._state_is_selected

    def name(self):
        return self._name


class Tile2(QLabel):
    def __init__(self, name, impath, **kwargs):
        super(Tile2, self).__init__(parent=kwargs.get("parent", None))
        self._name = name
        self._impath = impath
        self._pixmap = QtGui.QPixmap(self._impath)
        self.setPixmap(self._pixmap)

    def scale(self, factor):
        pixmap = QtGui.QPixmap(self._impath)
        width, height = pixmap.rect().width(), pixmap.rect().height()
        self._pixmap = pixmap.scaled(int(factor * width), int(factor * height), Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(self._pixmap)

    def set_size(self, width, height):
        pixmap = QtGui.QPixmap(self._impath)
        self._pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(self._pixmap)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = QMainWindow()

    # # Test Tile
    jerry1 = ImageButton(name="Jerry1", impath="jerry.png")
    jerry2 = ImageButton(name="Jerry2", impath="jerry.png")
    jerry3 = ImageButton(name="Jerry3", impath="jerry.png")
    jerry4 = ImageButton(name="Jerry4", impath="jerry.png")
    # jerry.scale(2)
    # jerry.show()

    # Test Cell
    volume = Cell(name="(0,0)", widget_capacity=3)
    volume.add_widget(jerry1)
    volume.add_widget(jerry2)
    volume.add_widget(jerry3)
    volume.add_widget(jerry4)
    # volume.show()

    window.setCentralWidget(volume)
    window.show()

    # g = Gridworld(5, 5)
    # g.show()
    sys.exit(app.exec())
