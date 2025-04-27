import time
import threading
from database import save_solution, record_time

solutions = []

def is_safe(board, row, col):
    for i in range(row):
        if board[i] == col or \
           board[i] - i == col - row or \
           board[i] + i == col + row:
            return False
    return True

def solve_sequential():
    global solutions
    solutions = []
    start_time = time.time()
    def solve(row=0, board=[]):
        if row == 8:
            solutions.append(tuple(board))
            save_solution(str(board))
            return
        for col in range(8):
            if is_safe(board, row, col):
                solve(row + 1, board + [col])
    solve()
    end_time = time.time()
    record_time("sequential", end_time - start_time)

def solve_threaded():
    global solutions
    solutions = []
    start_time = time.time()
    threads = []

    def solve(row=0, board=[]):
        if row == 8:
            solutions.append(tuple(board))
            save_solution(str(board))
            return
        for col in range(8):
            if is_safe(board, row, col):
                solve(row + 1, board + [col])

    for col in range(8):
        t = threading.Thread(target=solve, args=(1, [col]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    record_time("threaded", end_time - start_time)
