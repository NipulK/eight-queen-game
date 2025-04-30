import unittest
import os
from database import init_db, save_solution, get_stored_solutions, recognize_solution, reset_solutions

class TestDatabaseOperations(unittest.TestCase):
    def setUp(self):
        init_db()
        reset_solutions()

    def test_save_and_fetch_solution(self):
        sample_solution = "0,4,7,5,2,6,1,3"
        save_solution(sample_solution)
        solutions = get_stored_solutions()
        self.assertIn((sample_solution, None, 0), solutions)

    def test_recognize_solution(self):
        solution = "1,3,5,7,2,0,6,4"
        save_solution(solution)
        success, msg = recognize_solution(solution, "TestPlayer")
        self.assertTrue(success)
        self.assertEqual(msg, "Solution recognized!")

    def test_duplicate_solution(self):
        solution = "2,4,6,0,3,1,7,5"
        save_solution(solution)
        save_solution(solution)  # Should be ignored
        solutions = get_stored_solutions()
        matches = [s for s in solutions if s[0] == solution]
        self.assertEqual(len(matches), 1)

if __name__ == '__main__':
    unittest.main()
