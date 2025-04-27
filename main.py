import sys
from PyQt5.QtWidgets import QApplication
from database import init_db
from ui import GameUI

def main():
    init_db()
    app = QApplication(sys.argv)
    game = GameUI()
    game.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
