import sys
import re

class Game:
    def __init__(self, opener):
        self.opener = opener
        self.moves = []

    def add_move(self, move):
        self.moves.append(move)

    def set_winner(self, number, winner):
        self.number = number
        self.winner = winner


    def __repr__(self):
        return 'Game: {0} started with {1}, was won by {3} & had {2} moves'.format(self.number, self.opener, len(self.moves), self.winner)


with open(sys.argv[1]) as fd:
    red = 0
    blue = 0
    green = 0
    
    games = []
    best_starts=[0,0,0,0,0,0,0]

    player_re = re.compile('(BLUE|RED)')
    number_re = re.compile('\d+')
    winner_re = re.compile('(RED:\d+|BLUE:\d+|GREEN:\d+)')
    goes_re = re.compile('goes \d')

    for rl in fd:
        l=rl.strip()
        move = re.search('move[(]\d+[)]', l)
        if move:
            move_actual = int(number_re.search(move.group(0)).group(0))
            player = player_re.search(l).group(0)
            column = int(number_re.search(goes_re.search(l).group(0)).group(0))
            if move_actual == 1:
                game = Game(player)
            game.add_move(column)
            #print('move {0} player {1} goes {2}'.format(move_actual, player, column))
        result = re.search('Result of game \d+', l)
        if result:
            game_number = int(number_re.search(result.group(0)).group(0))
            winner = ''
            for win in winner_re.finditer(l):
                score = int(number_re.search(win.group(0)).group(0))
                if win.group(0).startswith('RED:') and score > red:
                    red += 1
                    winner = 'RED'
                elif win.group(0).startswith('BLUE:') and score > blue:
                    blue += 1
                    winner = 'BLUE'
                elif win.group(0).startswith('GREEN:') and score > green:
                    green += 1
                    winner = 'GREEN'
            game.set_winner(game_number, winner)
            games.append(game)
            #print('game {0} red {1} blue {2} green {3}'.format(game_number, red, blue, green))
            if game_number >= 3000:
                print(game_number)
                break

    for g in games:
        if g.winner == g.opener:
            print('Won serve: {}'.format(g))
            print(g.moves)
            best_starts[g.moves[0]] += 1
        elif g.winner != 'GREEN':
            print('Broke serve: {}'.format(g))

    print(best_starts)
