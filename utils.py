def format_solution(board):
    display = ""
    for row in range(8):
        line = ""
        for col in range(8):
            if board[row] == col:
                line += "Q "
            else:
                line += ". "
        display += line.strip() + "\n"
    return display.strip()
