import curses
import time
from random import choice

ROWS = 6
COLS = 7
TOP_ROW_IDX = 5

RED = 1
BLUE = 2
GREEN = 3
CHOICES = [x for x in range(0,7)]

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

def is_move_valid(col):
    return get_piece(TOP_ROW_IDX, col) == 0


def make_move(col, piece):
    for rx in range(0,6):
        if get_piece(rx, col) == 0:
            set_piece(rx, col, piece)
            break


def moves_remaining():
    return board.count(0)


def swap_player(player):
    if player == RED:
        return BLUE
    else:
        return RED


def find_winner():
    # check horizontal
    for rx in ([0,1,2,3,4,5]):
        for cx in ([0,1,2,3]):
            piece = get_piece(rx, cx)
            if piece != 0 and get_piece(rx, cx+1) == piece and get_piece(rx, cx+2) == piece and get_piece(rx, cx+3) == piece:
                return piece, (rx, cx), (rx, cx+1), (rx, cx+2), (rx, cx+3)
    # pure vertical
    for rx in ([0,1,2]):
        for cx in ([0,1,2,3,4,5,6]):
            piece = get_piece(rx, cx)
            if piece != 0 and get_piece(rx+1, cx) == piece and get_piece(rx+2, cx) == piece and get_piece(rx+3, cx) == piece:
                return piece, (rx, cx), (rx+1, cx), (rx+2, cx), (rx+3, cx)
    # forward slope
    for rx in ([0,1,2]):
        for cx in ([0,1,2,3]):
            piece = get_piece(rx, cx)
            if piece != 0 and get_piece(rx+1, cx+1) == piece and get_piece(rx+2, cx+2) == piece and get_piece(rx+3, cx+3) == piece:
                return piece, (rx, cx), (rx+1, cx+1), (rx+2, cx+2), (rx+3, cx+3)

    # backward slope    
    for rx in ([0,1,2]):
        for cx in ([3,4,5,6]):
            piece = get_piece(rx, cx)
            if piece != 0 and get_piece(rx+1, cx-1) == piece and get_piece(rx+2, cx-2) == piece and get_piece(rx+3, cx-3) == piece:
                return piece, (rx, cx), (rx+1, cx-1), (rx+2, cx-2), (rx+3, cx-3)
                
       
def show_winner(winner):
    piece = winner[0]
    for w in winner[1:]:
        set_piece(w[0], w[1], GREEN)
         

def draw_board(wx, red_colour, blue_colour, green_colour):
    wx.clear()
    wx.box()
    for rx in range(0, 6):
        for cx in range(0, 7):
            piece = get_piece(rx, cx)
            if piece == RED:
                draw_piece(wx, rx, cx, red_colour)
            elif piece == BLUE:
                draw_piece(wx, rx, cx, blue_colour)
            elif piece == GREEN:
                draw_piece(wx, rx, cx, green_colour)

    wx.refresh()


def main(screen):
    curses.initscr()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    colour1 = curses.color_pair(1)
    colour2 = curses.color_pair(2)
    colour3 = curses.color_pair(3)
    colour4 = curses.color_pair(4)
    prev_curses = curses.curs_set(0)

    screen.refresh()

    win = curses.newwin(ROWS + 2, COLS + 2 + (COLS - 1), 1, 1)
    win.bkgd(colour1)

    player = RED
    winner = None
    while winner is None and moves_remaining() > 0:
        move = choice(CHOICES)
        while not is_move_valid(move):
            move = choice(CHOICES)
        make_move(move, player)

        draw_board(win, colour2, colour3, colour4)
        winner = find_winner()
        if winner is None:
            player = swap_player(player)
            time.sleep(0.1)
        else:
            show_winner(winner)
            draw_board(win, colour2, colour3, colour4)

    ch = screen.getch()

    curses.curs_set(prev_curses)


try:
    curses.wrapper(main)
except:
    exit()
