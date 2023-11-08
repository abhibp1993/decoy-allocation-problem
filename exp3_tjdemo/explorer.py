import functools
from mywidgets import *

__author__ = "Abhishek N. Kulkarni"


class TJDecoyAllocExplorer(QMainWindow):
    def __init__(self, tsys, gw_params):
        """
        :param tsys: (dict) Serialized game on graph model.
        :param gw_params: (dict) Parameters of the gridworld game.
        """
        super(TJDecoyAllocExplorer, self).__init__()

        # Extract parameters
        self.rows = gw_params["rows"]
        self.cols = gw_params["cols"]
        self.obstacles = gw_params["obstacles"]
        self.real_cheese = gw_params["real_cheese"]

        # Properties
        self._selected_control = None

        # Set up the window
        self.window_title = "Tom & Jerry Decoy Allocation Explorer"
        self.setWindowTitle(self.window_title)

        # Set up the main widget
        self._main_layout = QVBoxLayout()

        # Add place buttons
        self._controls_layout = QHBoxLayout()
        self._controls_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._controls = [
            ImageButton(name="place_tom", impath="tom.png", parent=self),
            ImageButton(name="place_jerry", impath="jerry.png", parent=self),
            ImageButton(name="place_fake", impath="fake.jpg", parent=self),
            ImageButton(name="place_trap", impath="trap.jpg", parent=self)
        ]

        for control in self._controls:
            control.setFixedWidth(40)
            control.setFixedHeight(40)
            control.mousePressEvent = functools.partial(self._control_select_changed, control=control)
            self._controls_layout.addWidget(control)

        self._main_layout.addLayout(self._controls_layout)

        # Add gridworld
        self._gridworld = Gridworld(
            rows=self.rows,
            cols=self.cols,
            obstacles=self.obstacles,
            real_cheese=self.real_cheese
        )
        for cell in self._gridworld.cells():
            cell.mousePressEvent = functools.partial(self._cell_clicked, cell=cell)

        self._main_layout.addWidget(self._gridworld)

        # Set central widget
        central_widget = QWidget(self)
        central_widget.setLayout(self._main_layout)
        self.setCentralWidget(central_widget)

    def _control_select_changed(self, e, control):
        if control.is_selected():
            control.set_selected(False)
            self._selected_control = None
        else:
            control.set_selected(True)
            self._selected_control = control
            for other_control in self._controls:
                if other_control != control:
                    other_control.set_selected(False)

    def _cell_clicked(self, e, cell):
        print("placing in ", cell)
        if self._selected_control is not None and self._selected_control.name() == "place_fake":
            # If fake target exists in cell, remove it. Else, add it.
            if cell.has_widget(f"fake@{cell.name()}"):
                cell.remove_widget(f"fake@{cell.name()}")
            else:
                fake = ImageButton(f"fake@{cell.name()}", "fake.jpg", parent=cell)
                fake.mousePressEvent = functools.partial(self._cell_clicked, cell=cell)
                # fake.setFixedSize(40, 40)
                cell.add_widget(fake)


def main():
    # Load model
    gw_params = {
        "rows": 5,
        "cols": 5,
        "obstacles": [(1, 1), (2, 1), (3, 1), (4, 1)],
        "real_cheese": [(1, 4), (4, 4)]
    }

    # Instantiate gridworld game
    app = QApplication(sys.argv)
    explorer = TJDecoyAllocExplorer(
        tsys=None,
        gw_params=gw_params
    )
    explorer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
