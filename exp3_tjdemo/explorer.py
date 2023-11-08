import functools
import sys

import PyQt6
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
    QFileDialog,
    QSizePolicy
)
from mywidgets import ImageButton

__author__ = "Abhishek N. Kulkarni"


class TJDecoyAllocExplorer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Game parameters

        # Simulator properties
        self._selected_tile = None

        # Set up the window
        # self.setMinimumSize(800, 600)
        self.setWindowTitle("Tom & Jerry Decoy Allocation Explorer")

        # Set up the main widget
        self._main_layout = QVBoxLayout()

        # Set central widget
        central_widget = QWidget(self)
        central_widget.setLayout(self._main_layout)
        self.setCentralWidget(central_widget)

        # Add object buttons (tiles)
        self._tiles_layout = QHBoxLayout()
        self._tiles_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._tiles = []
        self._generate_tiles()
        self._main_layout.addLayout(self._tiles_layout)

        # Add gridworld
        self._gridworld = Gridworld(name="Gridworld", rows=5, cols=5)
        self._main_layout.addWidget(self._gridworld)

    def tile_select_changed(self, e, tile):
        if tile.is_selected():
            tile.set_selected(False)
            self._selected_tile = None
        else:
            tile.set_selected(True)
            self._selected_tile = tile
            for other_tile in self._tiles:
                if other_tile != tile:
                    other_tile.set_selected(False)

    def _generate_tiles(self):
        self._tiles = [
            ImageButton(name="place_tom", impath="tom.png", parent=self),
            ImageButton(name="place_jerry", impath="jerry.png", parent=self),
            ImageButton(name="place_fake", impath="fake.jpg", parent=self),
            ImageButton(name="place_trap", impath="trap.jpg", parent=self)
        ]

        for control in self._tiles:
            control.setFixedWidth(40)
            control.setFixedHeight(40)
            control.mousePressEvent = functools.partial(self.tile_select_changed, tile=control)
            self._tiles_layout.addWidget(control)

        self._tiles[0].setEnabled(False)
        self._tiles[1].setEnabled(False)


class Gridworld(QWidget):
    def __init__(self, name, rows, cols, **kwargs):
        super().__init__(parent=kwargs.get("parent", None))

        # Properties
        self._name = name
        self._rows = rows
        self._cols = cols

        # Default properties
        self.setMinimumWidth(50 * self._cols)
        self.setMinimumHeight(50 * self._rows)
        self.setContentsMargins(0, 0, 0, 0)

        # Create grid
        self._grid = QGridLayout()
        self._grid.setSpacing(0)
        self._grid.setContentsMargins(0, 0, 0, 0)

        self._cells = dict()
        for r in range(self._rows):
            for c in range(self._cols):
                self._cells[(r, c)] = Cell(f"({r}, {c})", parent=self)
                # self._cells[(r, c)].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self._cells[(r, c)].setStyleSheet(
                    "border: 1px solid black;"
                    # "background-color: white;"
                    "min-width=50px;"
                    "min-height=50px;"
                    "padding: 0px;"
                )
                self._grid.addWidget(self._cells[(r, c)], r, c)

        self.setLayout(self._grid)


class Cell(QPushButton):
    def __init__(self, name, **kwargs):
        super().__init__(parent=kwargs.get("parent", None))
        self.setMouseTracking(True)

        # Properties
        self._name = name

        # Default properties
        self.setFixedWidth(100)
        self.setFixedHeight(100)
        self.setContentsMargins(0, 0, 0, 0)

        # Main layout
        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)

        # Add label
        self._label = QLabel(self._name, self)
        self._label.setMargin(0)
        self._main_layout.addWidget(self._label)

        # Add two horizontal layouts to accommodate four tiles (at most). -- HARD CODED LIMIT.
        self._top_layout = QHBoxLayout()
        self._bottom_layout = QHBoxLayout()
        self._main_layout.addLayout(self._top_layout)
        self._main_layout.addLayout(self._bottom_layout)

        # Test tiles
        tom = ImageButton(name="tom", impath="tom.png", parent=self)
        jerry = ImageButton(name="jerry", impath="jerry.png", parent=self)
        fake = ImageButton(name="fake", impath="fake.jpg", parent=self)
        trap = ImageButton(name="trap", impath="trap.jpg", parent=self)

        tom.mousePressEvent = functools.partial(self._clicked, control=tom)
        jerry.mousePressEvent = functools.partial(self._clicked, control=jerry)

        self._top_layout.addWidget(tom)
        self._top_layout.addWidget(jerry)
        self._bottom_layout.addWidget(fake)
        self._bottom_layout.addWidget(trap)

    def enterEvent(self, e) -> None:
        # print("mouse enter event")
        self.setStyleSheet(
            "background-color: red;"
            "border: 1px solid black;"
        )

    def leaveEvent(self, e) -> None:
        # print("mouse exit")
        self.setStyleSheet(
            "background-color: white;"
            "border: 1px solid black;"
        )

    def mousePressEvent(self, e) -> None:
        print("mouse press event", self)

    def _clicked(self, e, control):
        print("clicked", control.name())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TJDecoyAllocExplorer()
    ex.show()
    sys.exit(app.exec())
