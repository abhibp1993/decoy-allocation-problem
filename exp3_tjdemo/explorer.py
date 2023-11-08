import functools
import sys

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
    QDockWidget
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

        # Add object buttons
        self._tiles_layout = QHBoxLayout()
        self._tiles_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
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
        self._main_layout.addLayout(self._tiles_layout)

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TJDecoyAllocExplorer()
    ex.show()
    sys.exit(app.exec())
