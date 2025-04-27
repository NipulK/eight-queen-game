import time
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, QGridLayout
)
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt
from solver import solve_sequential, solve_threaded
from database import recognize_solution, all_solutions_recognized, reset_solutions, get_stored_data  # Assuming this function exists
from utils import format_solution

BOARD_SIZE = 8  # 8x8 board

class GameUI(QWidget):
    def __init__(self):
        super().__init__()
        self.board = [-1] * BOARD_SIZE  # -1 means no queen in that row
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Eight Queens Puzzle')
        self.layout = QVBoxLayout()

        self.instructions = QLabel('Click to place queens! (one per row)')
        self.layout.addWidget(self.instructions)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter your name')
        self.layout.addWidget(self.name_input)

        self.board_grid = QGridLayout()
        self.board_buttons = [[QPushButton() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                btn = self.board_buttons[row][col]
                btn.setFixedSize(50, 50)
                btn.setStyleSheet("background-color: white;")
                btn.clicked.connect(lambda _, r=row, c=col: self.place_queen(r, c))
                self.board_grid.addWidget(btn, row, col)
        self.layout.addLayout(self.board_grid)

        self.submit_button = QPushButton('Submit Solution')
        self.submit_button.clicked.connect(self.submit_solution)
        self.layout.addWidget(self.submit_button)

        self.sequential_button = QPushButton('Solve Sequentially')
        self.sequential_button.clicked.connect(self.run_sequential)
        self.layout.addWidget(self.sequential_button)

        self.threaded_button = QPushButton('Solve with Threads')
        self.threaded_button.clicked.connect(self.run_threaded)
        self.layout.addWidget(self.threaded_button)

        self.auto_solve_button = QPushButton('Auto Solve')
        self.auto_solve_button.clicked.connect(self.auto_solve)
        self.layout.addWidget(self.auto_solve_button)

        self.compare_button = QPushButton('Compare Algorithms')
        self.compare_button.clicked.connect(self.compare_algorithms)
        self.layout.addWidget(self.compare_button)

        # New button to view stored data
        self.view_data_button = QPushButton('View Stored Solutions')
        self.view_data_button.clicked.connect(self.view_data)
        self.layout.addWidget(self.view_data_button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.setLayout(self.layout)

    def place_queen(self, row, col):
        # Remove previous queen from this row
        for c in range(BOARD_SIZE):
            self.board_buttons[row][c].setText('')
        # Set the queen
        self.board_buttons[row][col].setText('♛')
        self.board[row] = col

    def run_sequential(self):
        solve_sequential()
        QMessageBox.information(self, "Done", "Sequential solving completed and saved!")

    def run_threaded(self):
        solve_threaded()
        QMessageBox.information(self, "Done", "Threaded solving completed and saved!")

    def submit_solution(self):
        try:
            player_name = self.name_input.text().strip()
            if not player_name:
                QMessageBox.warning(self, "Error", "Name cannot be empty.")
                return
            if any(col == -1 for col in self.board):
                QMessageBox.warning(self, "Error", "You must place a queen in every row.")
                return
            if len(set(self.board)) != BOARD_SIZE:
                QMessageBox.warning(self, "Error", "Queens must be in different columns.")
                return

            formatted = str(self.board)
            success, msg = recognize_solution(formatted, player_name)
            if success:
                QMessageBox.information(self, "Success", f"Correct! {msg}")
            else:
                QMessageBox.warning(self, "Already Recognized", f"{msg}")

            if all_solutions_recognized():
                QMessageBox.information(self, "Completed", "All solutions recognized! Resetting...")
                reset_solutions()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def auto_solve(self):
        solution = []

        def is_safe(row, col):
            for r, c in enumerate(solution):
                if c == col or abs(c - col) == abs(r - row):
                    return False
            return True

        def solve(row=0):
            if row == BOARD_SIZE:
                return True
            cols = list(range(BOARD_SIZE))
            random.shuffle(cols)  # Shuffle columns for randomness
            for col in cols:
                if is_safe(row, col):
                    solution.append(col)
                    if solve(row + 1):
                        return True
                    solution.pop()
            return False

        if solve():
            self.board = solution.copy()
            # Update UI
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    self.board_buttons[r][c].setText('')
            for r in range(BOARD_SIZE):
                self.board_buttons[r][solution[r]].setText('♛')
            QMessageBox.information(self, "Solved", "A new solution has been auto-filled! 🎉")
        else:
            QMessageBox.warning(self, "Failed", "Could not find a solution.")

    def compare_algorithms(self):
        self.output.append("Comparing algorithms...\n")
        print("Comparing algorithms...")

        # Sequential timing
        start_seq = time.time()
        solve_sequential()
        end_seq = time.time()
        sequential_time = end_seq - start_seq

        # Threaded timing
        start_thr = time.time()
        solve_threaded()
        end_thr = time.time()
        threaded_time = end_thr - start_thr

        # Determine better
        if sequential_time < threaded_time:
            winner = "Sequential"
        else:
            winner = "Threaded"

        result_text = (
            f"Sequential Time: {sequential_time:.4f} seconds\n"
            f"Threaded Time: {threaded_time:.4f} seconds\n"
            f"Best Algorithm: {winner} 🎯"
        )

        self.output.append(result_text)
        print(result_text)

    def view_data(self):
        try:
            # Fetch stored solutions from the database
            stored_data = get_stored_data()  # Assuming this function exists
            if stored_data:
                data_text = "\n".join([str(solution) for solution in stored_data])
                self.output.setText(data_text)
            else:
                self.output.setText("No stored solutions found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve data: {str(e)}")
