import sys
from PyQt5.QtWidgets import QApplication
from database import init_db
from ui import GameUI
from database import get_stored_solutions


def main():
    init_db()
    app = QApplication(sys.argv)
    game = GameUI()
    game.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
