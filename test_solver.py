import unittest
from solver import is_safe

class TestEightQueens(unittest.TestCase):

    def test_is_safe(self):
        board = [0]
        self.assertFalse(is_safe(board, 1, 0))  # Same column
        self.assertFalse(is_safe(board, 1, 1))  # Same diagonal
        self.assertTrue(is_safe(board, 1, 2))   # Safe

if __name__ == '__main__':
    unittest.main()

