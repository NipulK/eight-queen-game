import unittest
from database import record_time
import time
import sqlite3
import matplotlib.pyplot as plt

execution_times = {}

class TestPerformanceRecording(unittest.TestCase):
    def test_record_time(self):
        method_name = "BacktrackingTest"
        start = time.time()
        time.sleep(0.1)  # Simulated work
        end = time.time()
        elapsed = end - start
        record_time(method_name, elapsed)

        conn = sqlite3.connect("eight_queens.db")
        c = conn.cursor()
        c.execute("SELECT time_taken FROM times WHERE method = ?", (method_name,))
        row = c.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertGreater(row[0], 0)

        # Store execution time for graph
        execution_times[method_name] = elapsed


# After test run, plot result
def plot_results():
    methods = list(execution_times.keys())
    times = list(execution_times.values())

    plt.figure(figsize=(6, 4))
    plt.bar(methods, times, color='orange')
    plt.title("Unit Test Performance Comparison")
    plt.ylabel("Execution Time (s)")
    plt.xlabel("Method")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    unittest.main(exit=False)  # Run test without exiting interpreter
    plot_results()             # Plot after test
