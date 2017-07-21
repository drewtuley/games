import curses
import time

ROWS = 6
COLS = 7

RED = 1
BLUE = 2

board = [0 for ix in range(ROWS * COLS)]


def piece_index(row, col):
    return row * 7 + col


def get_piece(row, col):
    idx = piece_index(row, col)
    if idx < len(board):
        return board[idx]


def set_piece(row, col, piece):
    board[piece_index(row, col)] = piece


def calc_screen_pos(game_row, game_col):
    return (6 - game_row, 1 + (game_col * 2))


def draw_piece(wx, game_row, game_col, colour):
    screen_row, screen_col = calc_screen_pos(game_row, game_col)
    wx.addch(screen_row, screen_col, curses.ACS_DIAMOND, colour)


def draw_board(wx, red_colour, blue_colour):
    wx.clear()
    wx.box()
    for rx in range(0, 6):
        for cx in range(0, 7):
            piece = get_piece(rx, cx)
            if piece == RED:
                draw_piece(wx, rx, cx, red_colour)
            elif piece == BLUE:
                draw_piece(wx, rx, cx, blue_colour)

    wx.refresh()


def main(screen):
    curses.initscr()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    colour1 = curses.color_pair(1)
    colour2 = curses.color_pair(2)
    colour3 = curses.color_pair(3)
    prev_curses = curses.curs_set(0)

    screen.refresh()

    win = curses.newwin(ROWS + 2, COLS + 2 + (COLS - 1), 1, 1)
    win.bkgd(curses.color_pair(1))

    set_piece(0, 0, RED)
    set_piece(1, 0, BLUE)
    draw_board(win, colour2, colour3)

    ch = screen.getch()

    curses.curs_set(prev_curses)


try:
    curses.wrapper(main)
except:
    exit()
