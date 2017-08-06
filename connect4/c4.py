import copy
import curses
import logging
import sys
import traceback
from random import choice

ROWS = 6
COLS = 7
TOP_ROW_IDX = 5

RED = 1
BLUE = 2
GREEN = 3
players = {RED: 'RED', BLUE: 'BLUE', GREEN: 'GREEN'}

CHOICES = [x for x in range(0, 7)]

board = [0 for ix in range(ROWS * COLS)]


def piece_index(row, col):
    return row * COLS + col


def get_piece_tuple(tpl):
    return get_piece(tpl[0], tpl[1])


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


def dump_board():
    logging.debug('0123456')
    for rx in [5,4,3,2,1,0]:
        row = ''
        for cx in [0,1,2,3,4,5,6]:
            piece = get_piece(rx, cx)
            if piece == RED:
                row += 'R'
            elif piece == BLUE:
                row += 'B'
            elif piece == GREEN:
                row += '*'
            else:
                row += ' '
        logging.debug(row)
    logging.debug('0123456')


def is_move_valid(col):
    return get_piece(TOP_ROW_IDX, col) == 0


def make_move(col, piece):
    for rx in range(0, 6):
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


def get_player_name(player):
    return players[player]


def precalc_winning_nodes():
    # check horizontal
    for rx in ([0, 1, 2, 3, 4, 5]):
        for cx in ([0, 1, 2, 3]):
            yield (rx, cx), piece_index(rx, cx), piece_index(rx, cx + 1), piece_index(rx, cx + 2), piece_index(rx,
                                                                                                               cx + 3)
    # pure vertical
    for rx in ([0, 1, 2]):
        for cx in ([0, 1, 2, 3, 4, 5, 6]):
            yield (rx, cx), piece_index(rx, cx), piece_index(rx + 1, cx), piece_index(rx + 2, cx), piece_index(rx + 3,
                                                                                                               cx)
    # forward slope
    for rx in ([0, 1, 2]):
        for cx in ([0, 1, 2, 3]):
            yield (rx, cx), piece_index(rx, cx), piece_index(rx + 1, cx + 1), piece_index(rx + 2, cx + 2), piece_index(
                rx + 3, cx + 3)
    # backward slope    
    for rx in ([0, 1, 2]):
        for cx in ([3, 4, 5, 6]):
            yield (rx, cx), piece_index(rx, cx), piece_index(rx + 1, cx - 1), piece_index(rx + 2, cx - 2), piece_index(
                rx + 3, cx - 3)


def find_winner():
    empty_above = {}
    for nodes in connect4_nodes:
        if len(empty_above) == COLS:
            break
        if nodes[0][1] not in empty_above:
            piece = board[nodes[1]]
            if piece != 0:
                if board[nodes[2]] == piece and board[nodes[3]] == piece and board[nodes[4]] == piece:
                    return piece, nodes[1], nodes[2], nodes[3], nodes[4]
            else:
                empty_above[nodes[0][1]] = True


def show_winner(winner):
    piece = winner[0]
    for w in winner[1:]:
        # set_piece(w[0], w[1], GREEN)
        board[w] = GREEN


def draw_board(wx, c_map):
    wx.clear()
    wx.box()
    for rx in range(0, 6):
        for cx in range(0, 7):
            piece = get_piece(rx, cx)
            try:
                colour = c_map[piece]
                draw_piece(wx, rx, cx, colour)
            except KeyError:
                pass

    wx.refresh()


def clear_board():
    for x in range(ROWS * COLS):
        board[x] = 0


def random_move():
    move = choice(CHOICES)
    while not is_move_valid(move):
        move = choice(CHOICES)
    return move


def restore_board(stash):
    for ix in range(ROWS * COLS):
        board[ix] = stash[ix]


def rule0(player, move):
    logging.debug('rule0: {}'.format(get_player_name(player)))
    return [random_move()]


def rule1(player, move):
    """Can player win in 1 move"""
    logging.debug('rule1: {}'.format(get_player_name(player)))
    win_moves = []
    for cx in range(0, COLS):
        if is_move_valid(cx):
            stash = copy.copy(board)
            make_move(cx, player)
            winner = find_winner()
            restore_board(stash)
            if winner is not None:
                logging.debug('rule1: {} has a winning move @ {}'.format(get_player_name(player), cx))
                win_moves.append(cx)
    return win_moves


def rule2(player, move):
    """Rule 1 for the other player (i.e. if he can win in 1 move I should stop him)"""
    logging.debug('rule2: {}'.format(get_player_name(player)))
    return rule1(swap_player(player), move)


def rule3(player, move):
    """ Can player win in 2 moves (if not stopped) """
    logging.debug('rule3: {}'.format(get_player_name(player)))
    for cx in range(0, COLS):
        if is_move_valid(cx):
            stash = copy.copy(board)
            make_move(cx, player)
            win_move2 = rule1(player, move)
            if len(win_move2) > 1:
                restore_board(stash)
                logging.debug(
                    'rule3: {} has a potentially winning move @ {} & {}'.format(get_player_name(player), cx, win_move2))
                return [cx]     # making this move opens up >1 possible wins
            # check if making this move will open up a winning position for the other player
            win_move_bad = rule2(player, move)
            restore_board(stash)
            if len(win_move2)>1  and len(win_move_bad) == 0:
                logging.debug(
                    'rule3: {} has a potentially winning move @ {} & {}'.format(get_player_name(player), cx, win_move2))
                return cx
    return []


def main(screen):
    logging.basicConfig(format='%(asctime)s %(message)s',
                        filename='c4.log', level=logging.DEBUG)
    logging.captureWarnings(True)

    for nodex in precalc_winning_nodes():
        print(nodex)

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

    colour_map = {RED: colour2, BLUE: colour3, GREEN: colour4}

    prev_curses = curses.curs_set(0)

    screen.refresh()

    win = curses.newwin(ROWS + 2, COLS + 2 + (COLS - 1), 1, 1)
    score_win = curses.newwin(3, COLS + 2 + (COLS - 1), 2 + ROWS + 1, 1)
    win.bkgd(colour1)
    score_win.bkgd(colour1)

    scores = {RED: 0, BLUE: 0, GREEN: 0}
    start_player = RED
    game = 1

    while True:
        clear_board()
        player = start_player
        draw_board(win, colour_map)
        winner = None
        move_num = 1
        while winner is None and moves_remaining() > 0:
            if player == RED:
                for rule in [rule1, rule2, rule3, rule0]:
                    moves = rule(player, move_num)
                    if len(moves) >0:
                        move = moves[0]
                        break
            else:       # has to be BLUE by default
                for rule in [rule0]:
                    moves = rule(player, move_num)
                    if len(moves) >0:
                        move = moves[0]
                        break

            logging.debug('move({}): player {} goes {}'.format(move_num, get_player_name(player), move))

            make_move(move, player)
            move_num += 1
            dump_board()

            draw_board(win, colour_map)
            winner = find_winner()
            if winner is None:
                player = swap_player(player)
                # time.sleep(0.01)
            else:
                win_piece = winner[0]
                scores[win_piece] += 1

                show_winner(winner)
                dump_board()
                draw_board(win, colour_map)
                # time.sleep(0.1)
        if winner is None:
            scores[GREEN] += 1
        score_win.box()
        score_win.addstr(1, 1, '{:04d}'.format(scores[RED]), colour2)
        score_win.addstr(1, 6, '{:03d}'.format(scores[GREEN]), colour4)
        score_win.addstr(1, 10, '{:04d}'.format(scores[BLUE]), colour3)
        logging.debug('Result of game {} - RED:{} BLUE:{} GREEN:{}'.format(game, scores[RED], scores[BLUE], scores[GREEN]))
        game += 1
        score_win.refresh()
        start_player = swap_player(start_player)

    curses.curs_set(prev_curses)


node_map = {}
for nodex in precalc_winning_nodes():
    if nodex[0] in node_map.keys():
        lst = node_map[nodex[0]]
    else:
        lst = []
    lst.append(nodex)
    node_map[nodex[0]] = lst

connect4_nodes = []
for node in sorted(node_map.keys()):
    for c4 in node_map[node]:
        connect4_nodes.append(c4)
for node in connect4_nodes:
    print('{}: {} {} {} {} {} {} {} {}'.format(node[0], node[1], board[node[1]], node[2], board[node[2]], node[3],
                                               board[node[3]], node[4], board[node[4]]))

try:
    curses.wrapper(main)
except Exception as e:
    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    print(e)
    traceback.print_exc()
    exit()
