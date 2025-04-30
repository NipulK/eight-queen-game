import time
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, QGridLayout, QScrollArea,
    QDialog
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

        self.hint_button = QPushButton('Hint')
        self.restart_button.setStyleSheet(button_style)
        self.hint_button.clicked.connect(self.show_hint)
        self.layout.addWidget(self.hint_button)

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
        self.output.append("Comparing algorithms over 10 runs each...\n")

        sequential_times = []
        threaded_times = []

        for i in range(10):
            self.output.append(f"Run {i+1}...\n")
            
            # Sequential timing
            start_seq = time.time()
            solve_sequential()
            end_seq = time.time()
            seq_time = end_seq - start_seq
            sequential_times.append(seq_time)

            # Threaded timing
            start_thr = time.time()
            solve_threaded()
            end_thr = time.time()
            thr_time = end_thr - start_thr
            threaded_times.append(thr_time)

        # Average times
        avg_seq = sum(sequential_times) / 10
        avg_thr = sum(threaded_times) / 10

        # Save to database
        from database import record_time
        record_time("Sequential", avg_seq)
        record_time("Threaded", avg_thr)

        # Display results
        result_text = (
            f"\n--- Results over 10 runs ---\n"
            f"Average Sequential Time: {avg_seq:.4f} seconds\n"
            f"Average Threaded Time: {avg_thr:.4f} seconds\n"
        )
        self.output.append(result_text)

        # Plot graph
        methods = ['Sequential', 'Threaded']
        times = [avg_seq, avg_thr]

        plt.figure(figsize=(6, 4))
        bars = plt.bar(methods, times, color=['skyblue', 'lightgreen'])
        for bar, time_val in zip(bars, times):
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.005, f'{time_val:.4f}', ha='center', va='bottom')

        plt.title("Average Time Comparison of Solving Algorithms (10 Runs)")
        plt.ylabel("Time (seconds)")
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()




    def view_data(self):
        """Display stored solutions in a popup window"""
        try:
            dialog = SolutionsDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display solutions: {str(e)}")

    def restart_game(self):
        """Reset the game to initial state"""
        self.board = [-1] * BOARD_SIZE
        self.name_input.clear()
        # Clear all queens from the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.board_buttons[row][col].setText('')
        self.output.clear()

    def show_hint(self):
        """Show a hint for the next safe queen placement"""
        for row in range(BOARD_SIZE):
            if self.board[row] == -1:
                for col in range(BOARD_SIZE):
                    if self.is_safe(row, col):
                        QMessageBox.information(self, "Hint", 
                            f"Try placing a queen at row {row + 1}, column {col + 1}.")
                        return
                break
        QMessageBox.warning(self, "Hint", "No safe position found.")

    def is_safe(self, row, col):
        """Check if it's safe to place a queen at the given position"""
        for r in range(row):
            c = self.board[r]
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True


class SolutionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stored Solutions")
        self.setModal(True)
        self.setGeometry(300, 300, 600, 400)
        self.setStyleSheet("background-color: #2b2b2b; color: #e0e0e0;")
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Eight Queens Solutions")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #e0e0e0;
            margin: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Solutions display
        self.solutions_text = QTextEdit()
        self.solutions_text.setReadOnly(True)
        self.solutions_text.setStyleSheet("""
            QTextEdit {
                background-color: #444;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                color: #e0e0e0;
                border: 2px solid #aaa;
            }
        """)
        layout.addWidget(self.solutions_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #616161;
                border: none;
                color: white;
                font-size: 16px;
                border-radius: 10px;
                padding: 10px;
                min-width: 100px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        self.load_solutions()
    
    def load_solutions(self):
        try:
            solutions = get_stored_solutions()
            if solutions:
                text = "=== Stored Solutions ===\n\n"
                for solution, recognized_by, recognized in solutions:
                    text += f"Solution: {solution}\n"
                    if recognized_by:
                        text += f"Recognized by: {recognized_by}\n"
                    text += f"Status: {'Recognized' if recognized else 'Not Recognized'}\n"
                    text += "=" * 40 + "\n\n"
            else:
                text = "No stored solutions found."
            
            self.solutions_text.setText(text)
        except Exception as e:
            self.solutions_text.setText(f"Error loading solutions: {str(e)}")
