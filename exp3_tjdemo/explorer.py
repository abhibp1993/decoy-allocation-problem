import ast
import functools
import game
import sys

from gwutils import *

# import PyQt6
# from PyQt6 import QtCore, QtGui, QtWidgets
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
    def __init__(self, gw_config, base_game):
        super().__init__()

        # Game parameters
        self._rows = gw_config["rows"]
        self._cols = gw_config["cols"]
        self._obstacles = gw_config["obstacles"]
        self._real_cheese = gw_config["real_cheese"]
        self._tom = gw_config["tom"]
        self._jerry = gw_config["jerry"]
        self._solver = gw_config["solver"]
        self._game = base_game

        # Simulator properties
        self._selected_tile = None

        # Set up the window
        self.setWindowTitle("Decoy Allocation Explorer")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Set up the main widget
        self._main_layout = QVBoxLayout()

        # Title
        self._title = QLabel("Decoy Allocation in Tom and Jerry Game")
        self._title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._title)

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
        self._gridworld = GridUI(name="Gridworld", rows=self._rows, cols=self._cols)
        self._main_layout.addWidget(self._gridworld)

        # Add obstacles
        for obs in self._obstacles:
            cell = self._gridworld[obs]
            cell.setStyleSheet("background-color: black;")
            cell.enterEvent = lambda e: None
            cell.leaveEvent = lambda e: None
            cell.mousePressEvent = lambda e: None

        # Add real cheese
        for cheese in self._real_cheese:
            cell = self._gridworld[cheese]
            cell.cheese.setVisible(True)
            cell.cheese.mousePressEvent = lambda e: None
            cell.mousePressEvent = lambda e: None

        # Add tom, jerry
        if self._tom is not None:
            self._gridworld[self._tom].tom.setVisible(True)

        if self._jerry is not None:
            self._gridworld[self._jerry].jerry.setVisible(True)

        # Add author
        self._author = QLabel("Abhishek N. Kulkarni")
        self._author.setStyleSheet("font-size: 10px; font-weight: bold;")
        self._author.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._main_layout.addWidget(self._author)

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
            ImageButton(name="place_trap", impath="trap.jpg", parent=self),
            ImageButton(name="run", impath="run.png", parent=self)
        ]

        for control in self._tiles:
            control.setFixedWidth(40)
            control.setFixedHeight(40)
            control.mousePressEvent = functools.partial(self.tile_select_changed, tile=control)
            self._tiles_layout.addWidget(control)

        # self._tiles[0].setEnabled(False)
        # self._tiles[1].setEnabled(False)
        self._tiles[4].mousePressEvent = lambda e: None


class GridUI(QWidget):
    def __init__(self, name, rows, cols, **kwargs):
        super().__init__(parent=kwargs.get("parent", None))

        # Properties
        self._name = name
        self._rows = rows
        self._cols = cols

        # Default properties
        # self.setMinimumWidth(120 * (self._cols + 1))
        # self.setMinimumHeight(120 * (self._rows + 1))
        self.setContentsMargins(5, 5, 5, 5)

        # Create grid
        self._grid = QGridLayout()
        self._grid.setSpacing(0)
        self._grid.setContentsMargins(0, 0, 0, 0)

        self._cells = dict()
        for r in range(self._rows):
            for c in range(self._cols):
                self._cells[(r, c)] = CellUI(f"({r}, {c})", parent=self)
                self._cells[(r, c)].setMinimumSize(100, 100)
                self._cells[(r, c)].setStyleSheet(
                    "border: 2px solid black;"
                    "background-color: white;"
                    "min-width=100px;"
                    "min-height=100px;"
                    # "padding: 0px;"
                )
                self._grid.addWidget(self._cells[(r, c)], r, c)

        self.setLayout(self._grid)

    def __getitem__(self, pos):
        return self._cells[pos]


class CellUI(QPushButton):
    def __init__(self, name, **kwargs):
        super().__init__(parent=kwargs.get("parent", None))
        self.setMouseTracking(True)

        # Properties
        self._name = name

        # Default properties
        # self.setFixedWidth(100)
        # self.setFixedHeight(100)
        self.setContentsMargins(0, 0, 0, 10)

        # Main layout
        self._main_layout = QGridLayout()
        self._main_layout.setRowStretch(0, 1)
        self._main_layout.setRowStretch(1, 3)
        self._main_layout.setRowStretch(2, 3)
        self.setLayout(self._main_layout)

        # Add label
        self._label = QLabel(self._name, self)
        self._label.setStyleSheet("border: 0px solid black;")
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._label.setMargin(0)
        self._main_layout.addWidget(self._label, 0, 0)

        # Test tiles
        self.tom = ImageButton(name="tom", impath="tom.png", parent=self)
        self.jerry = ImageButton(name="jerry", impath="jerry.png", parent=self)
        self.cheese = ImageButton(name="jerry", impath="cheese.png", parent=self)
        self.fake = ImageButton(name="fake", impath="fake.jpg", parent=self)
        self.trap = ImageButton(name="trap", impath="trap.jpg", parent=self)

        self.tom.setMinimumSize(40, 40)
        self.jerry.setMinimumSize(40, 40)
        self.cheese.setMinimumSize(40, 40)
        self.fake.setMinimumSize(40, 40)
        self.trap.setMinimumSize(40, 40)

        self.tom.setVisible(False)
        self.jerry.setVisible(False)
        self.cheese.setVisible(False)
        self.fake.setVisible(False)
        self.trap.setVisible(False)

        self.tom.mousePressEvent = functools.partial(self._clicked, control=self.tom)
        self.jerry.mousePressEvent = functools.partial(self._clicked, control=self.jerry)
        self.cheese.mousePressEvent = functools.partial(self._clicked, control=self.cheese)
        self.fake.mousePressEvent = functools.partial(self._clicked, control=self.fake)
        self.trap.mousePressEvent = functools.partial(self._clicked, control=self.trap)

        self._main_layout.addWidget(self.cheese, 0, 1)
        self._main_layout.addWidget(self.tom, 1, 0)
        self._main_layout.addWidget(self.jerry, 1, 1)
        self._main_layout.addWidget(self.fake, 2, 0)
        self._main_layout.addWidget(self.trap, 2, 1)

    def enterEvent(self, e) -> None:
        self.setStyleSheet(
            "background-color: white;"
            "border: 5px solid green;"
        )
        self._label.setStyleSheet("border: 0px solid black;")

    def leaveEvent(self, e) -> None:
        self.setStyleSheet(
            "background-color: white;"
            "border: 2px solid black;"
        )
        self._label.setStyleSheet("border: 0px solid black;")

    def mousePressEvent(self, e) -> None:
        print("mouse press event", self, self.parent().parent())
        window = self.parent().parent().parent()
        selected_tile = window._selected_tile.name() if window._selected_tile is not None else None
        if selected_tile is not None:
            if selected_tile == "place_tom":
                tom_pos = window._tom
                if tom_pos is not None:
                    window._gridworld[tom_pos].tom.setVisible(False)
                self.tom.setVisible(True)
                window._tom = ast.literal_eval(self._name)
            elif selected_tile == "place_jerry":
                jerry_pos = window._jerry
                if jerry_pos is not None:
                    window._gridworld[jerry_pos].jerry.setVisible(False)
                self.jerry.setVisible(True)
                window._jerry = ast.literal_eval(self._name)
            elif selected_tile == "place_fake":
                self.fake.setVisible(True)
            elif selected_tile == "place_trap":
                self.trap.setVisible(True)

    def _clicked(self, e, control):
        for idx in range(self._main_layout.count()):
            if self._main_layout.itemAt(idx).widget() == control:
                control.setVisible(False)


class Gridworld(game.Game):
    def __init__(self, dim, obs, real_cheese):
        super(Gridworld, self).__init__(type_game=game.TYPE_DTPTB)
        self.rows = dim[0]
        self.cols = dim[1]
        self.obs = obs
        self.real_cheese = real_cheese

    def __str__(self):
        delta = {(st, a): self.delta(st, a) for st in self.states() for a in self.actions(st)}
        final = {st for st in self.states() if self.final(st)}
        return f"{self.states()=}\n" \
               f"{delta=}\n" \
               f"{final=}\n"

    def init_states(self):
        """ (r1, c1): tom (defender), (r2, c2): jerry (attacker) """
        return [(r1, c1, r2, c2, t)
                for r1 in range(self.rows)
                for c1 in range(self.cols)
                for r2 in range(self.rows)
                for c2 in range(self.cols)
                for t in [1, 2]
                if (r1, c1) not in self.obs and (r2, c2) not in self.obs
                ]

    def is_state_valid(self, state) -> bool:
        r1, c1, r2, c2, t = state
        if (r1, c1) in self.obs and (r2, c2) in self.obs:
            return False

        if 0 <= r1 < self.rows and 0 <= c1 < self.cols and 0 <= r2 < self.rows and 0 <= c2 < self.cols:
            return True

    def turn(self, state):
        return state[-1]

    def actions(self, state=None):
        return [GW_ACT_N, GW_ACT_E, GW_ACT_S, GW_ACT_W]

    def delta(self, state, act):
        turn = self.turn(state)

        if state[0:2] == state[2:4]:
            return state[0:4] + ((1,) if turn == 2 else (2,))

        if turn == 1:
            r, c = state[0:2]
        else:
            r, c = state[2:4]

        next_r, next_c = move((r, c), act)
        next_r, next_c = bouncy_wall((r, c), [(next_r, next_c)], (self.rows, self.cols))[0]
        next_r, next_c = bouncy_obstacle((r, c), [(next_r, next_c)], self.obs)[0]

        if turn == 1:
            return (next_r, next_c) + state[2:4] + (2,)
        else:
            return state[0:2] + (next_r, next_c) + (1,)

    def final(self, state):
        return state in [(r1, c1, r2, c2, t)
                         for r2, c2 in self.real_cheese
                         for r1 in range(self.rows)
                         for c1 in range(self.cols)
                         for t in range(1, 3)
                         if (r2, c2) not in self.obs and (r1, c1) not in self.obs
                         ]

    def jerry_equiv(self, cell):
        """ Returns states in which Jerry is at given cell """
        return {
            (r1, c1) + cell + (t,)
            for r1 in range(self.rows)
            for c1 in range(self.cols)
            for t in range(1, 3)
            if (r1, c1) not in self.obs
        }

    def atoms(self):
        return {"caught", "cheese"}

    def label(self, state):
        r1, c1, r2, c2, t = state
        if (r1, c1) == (r2, c2):
            return {"caught"}
        elif (r2, c2) in self.real_cheese:
            return {"cheese"}
        else:
            return set()


def run_explorer(gw_config, base_game):
    app = QApplication(sys.argv)
    ex = TJDecoyAllocExplorer(gw_config, base_game)
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    # Define game configuration
    config = {
        "rows": 7,
        "cols": 7,
        "obstacles": [(0, 4), (2, 4), (4, 4), (6, 4)],
        "real_cheese": [(1, 6), (4, 6)],
        "tom": None,
        "jerry": None,
        "solver": "dswin",
    }

    # Define game
    gw = Gridworld(dim=(config["rows"], config["cols"]), obs=config["obstacles"], real_cheese=config["real_cheese"])
    model = gw.build_model()
    gw_graph = game.to_graph(model)


    # Run allocation explorer GUI
    run_explorer(gw_config=config, base_game=gw_graph)
