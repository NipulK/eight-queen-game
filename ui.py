import time
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, QGridLayout, QScrollArea
)
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPainter, QColor, QPixmap, QFont
from PyQt5.QtCore import Qt
from solver import solve_sequential, solve_threaded
from database import (
    recognize_solution,
    all_solutions_recognized,
    reset_solutions,
    get_stored_data,
    get_stored_solutions
)
from utils import format_solution


BOARD_SIZE = 8  # 8x8 board

class GameUI(QWidget):
    def __init__(self):
        super().__init__()
        self.board = [-1] * BOARD_SIZE  # -1 means no queen in that row
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Eight Queens Puzzle')
        self.setStyleSheet("background-color: #2b2b2b; color: #e0e0e0;")
        self.setGeometry(200, 200, 600, 700)

        # Main Layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)

        # Instructions Label with enhanced font style
        self.instructions = QLabel('Click to place queens! (one per row)')
        self.instructions.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #e0e0e0;
            text-align: center; padding: 15px; background-color: #444;
            border-radius: 8px;
        """)
        self.layout.addWidget(self.instructions)

        # Name Input with style
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter your name')
        self.name_input.setStyleSheet("""
            background-color: #444; border: 2px solid #aaa;
            border-radius: 10px; padding: 10px; font-size: 16px;
            color: #fff; margin-bottom: 20px;
        """)
        self.layout.addWidget(self.name_input)

        # Board Grid Layout with visual improvements
        self.board_grid = QGridLayout()
        self.board_buttons = [[QPushButton() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                btn = self.board_buttons[row][col]
                btn.setFixedSize(60, 60)
                # Set alternating colors for chess board pattern
                is_light_square = (row + col) % 2 == 0
                base_color = "#F0D9B5" if is_light_square else "#B58863"  # Classic chess colors
                hover_color = "#BCE784" if is_light_square else "#8EAF6F"  # Green highlight on hover
                
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {base_color};
                        color: #2C3E50;
                        border: 1px solid #34495E;
                        border-radius: 0px;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_color};
                        border: 2px solid #2980B9;
                    }}
                    QPushButton:pressed {{
                        background-color: #E74C3C;
                        border: 2px solid #C0392B;
                    }}
                """)
                btn.clicked.connect(lambda _, r=row, c=col: self.place_queen(r, c))
                self.board_grid.addWidget(btn, row, col)

        self.layout.addLayout(self.board_grid)

        # Action Buttons Layout (Submit, Solve, etc.)
        button_style = """
        QPushButton {
            background-color: #616161;
            border: none;
            color: white;
            font-size: 16px;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #757575;
        }
        QPushButton:pressed {
            background-color: #424242;
        }
        """

        self.submit_button = QPushButton('Submit Solution')
        self.submit_button.setStyleSheet(button_style)
        self.submit_button.clicked.connect(self.submit_solution)

        self.sequential_button = QPushButton('Solve Sequentially')
        self.sequential_button.setStyleSheet(button_style)
        self.sequential_button.clicked.connect(self.run_sequential)

        self.threaded_button = QPushButton('Solve with Threads')
        self.threaded_button.setStyleSheet(button_style)
        self.threaded_button.clicked.connect(self.run_threaded)

        self.auto_solve_button = QPushButton('Auto Solve')
        self.auto_solve_button.setStyleSheet(button_style)
        self.auto_solve_button.clicked.connect(self.auto_solve)

        self.compare_button = QPushButton('Compare Algorithms')
        self.compare_button.setStyleSheet(button_style)
        self.compare_button.clicked.connect(self.compare_algorithms)

        self.view_data_button = QPushButton('View Stored Solutions')
        self.view_data_button.setStyleSheet(button_style)
        self.view_data_button.clicked.connect(self.view_data)

        self.restart_button = QPushButton('Restart Game')
        self.restart_button.setStyleSheet(button_style)
        self.restart_button.clicked.connect(self.restart_game)

        self.show_solutions_button = QPushButton('Show Stored Solutions')
        self.show_solutions_button.clicked.connect(self.show_stored_solutions)
        self.layout.addWidget(self.show_solutions_button)


        button_layout = QVBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.sequential_button)
        button_layout.addWidget(self.threaded_button)
        button_layout.addWidget(self.auto_solve_button)
        button_layout.addWidget(self.compare_button)
        button_layout.addWidget(self.view_data_button)
        button_layout.addWidget(self.restart_button)

        self.layout.addLayout(button_layout)

        # Output Display with a border and padding
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            background-color: #444; border-radius: 8px; padding: 15px;
            font-size: 14px; color: #e0e0e0; border: 2px solid #aaa;
        """)
        self.layout.addWidget(self.output)

        # Add Scroll Area for better content management
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container_widget = QWidget()
        container_widget.setLayout(self.layout)
        scroll_area.setWidget(container_widget)

        # Set the scroll area as the central layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def place_queen(self, row, col):
        for c in range(BOARD_SIZE):
            self.board_buttons[row][c].setText('')
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
                win_msg = QMessageBox()
                win_msg.setIcon(QMessageBox.Information)
                win_msg.setWindowTitle("🎉 Congratulations! 🎉")
                win_msg.setText(f"Amazing work, {player_name}!\nYou've successfully solved the Eight Queens Puzzle!")
                win_msg.setInformativeText("Would you like to play again?")
                win_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                win_msg.setDefaultButton(QMessageBox.Yes)
                
                if win_msg.exec_() == QMessageBox.Yes:
                    self.restart_game()
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
            random.shuffle(cols)
            for col in cols:
                if is_safe(row, col):
                    solution.append(col)
                    if solve(row + 1):
                        return True
                    solution.pop()
            return False

        if solve():
            self.board = solution.copy()
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

        # Sequential
        start_seq = time.time()
        solve_sequential()
        end_seq = time.time()
        sequential_time = end_seq - start_seq

        # Threaded
        start_thr = time.time()
        solve_threaded()
        end_thr = time.time()
        threaded_time = end_thr - start_thr

        # Log result text
        result_text = (
            f"Sequential Time: {sequential_time:.4f} seconds\n"
            f"Threaded Time: {threaded_time:.4f} seconds\n"
        )
        self.output.append(result_text)

        # Show bar chart
        methods = ['Sequential', 'Threaded']
        times = [sequential_time, threaded_time]

        plt.figure(figsize=(6, 4))
        plt.bar(methods, times, color=['skyblue', 'lightgreen'])
        plt.title("Comparison of Solving Algorithms")
        plt.ylabel("Time (seconds)")
        plt.show()

    def view_data(self):
        try:
            stored_data = get_stored_data()  # Assuming this function exists
            if stored_data:
                data_text = "\n".join([str(solution) for solution in stored_data])
                self.output.setText(data_text)
            else:
                self.output.setText("No stored solutions found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve data: {str(e)}")

    def restart_game(self):
        """Reset the game to initial state"""
        self.board = [-1] * BOARD_SIZE
        self.name_input.clear()
        # Clear all queens from the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.board_buttons[row][col].setText('')
        self.output.clear()
    def show_stored_solutions(self):
        try:
            solutions = get_stored_solutions()
            if not solutions:
                QMessageBox.information(self, "No Solutions", "No solutions stored yet.")
                return

            popup = QWidget()
            popup.setWindowTitle("Stored Solutions")
            layout = QVBoxLayout()

            for sol in solutions:
                solution_text = sol[0]
                recognized_by = sol[1] if sol[1] else "N/A"
                recognized_status = "Yes" if sol[2] == 1 else "No"
                label = QLabel(f"Solution: {solution_text} | Recognized by: {recognized_by} | Recognized: {recognized_status}")
                layout.addWidget(label)

            popup.setLayout(layout)
            popup.setMinimumSize(400, 300)
            popup.show()

        # Keep reference to popup so it doesn't close immediately
            self.popup_window = popup

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

