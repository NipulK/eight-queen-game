import unittest
import os
import sqlite3
from database import (
    init_db, save_solution, recognize_solution,
    all_solutions_recognized, reset_solutions
)
from solver import solve_sequential

DB_NAME = "eight_queens.db"

class TestEightQueensProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        # Clean up database before each test
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM solutions")
        c.execute("DELETE FROM times")
        conn.commit()
        conn.close()

    def test_sequential_solution_count(self):
        # Check if solve_sequential generates 92 unique solutions
        solutions = solve_sequential()
        self.assertEqual(len(solutions), 92)
        self.assertEqual(len(set(tuple(sol) for sol in solutions)), 92)

    def test_save_and_recognize_solution(self):
        test_solution = str([0, 4, 7, 5, 2, 6, 1, 3])
        save_solution(test_solution)

        # Try to recognize with player name
        success, msg = recognize_solution(test_solution, "Alice")
        self.assertTrue(success)
        self.assertIn("recognized", msg.lower())

        # Try again — should now say already recognized
        success, msg = recognize_solution(test_solution, "Bob")
        self.assertFalse(success)
        self.assertIn("already recognized", msg.lower())

    def test_all_solutions_recognized(self):
        test_solution = str([0, 4, 7, 5, 2, 6, 1, 3])
        save_solution(test_solution)
        self.assertFalse(all_solutions_recognized())

        recognize_solution(test_solution, "TestUser")
        self.assertTrue(all_solutions_recognized())

    def test_reset_solutions(self):
        test_solution = str([0, 4, 7, 5, 2, 6, 1, 3])
        save_solution(test_solution)
        recognize_solution(test_solution, "ResetUser")
        reset_solutions()

        # After reset, solution should not be recognized
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT recognized FROM solutions WHERE solution = ?", (test_solution,))
        result = c.fetchone()[0]
        conn.close()

        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
