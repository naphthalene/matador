import random
from base import Bot

class DumbBot(Bot):
    def guess(self, player, game):
        my_moves = game.moves.filter(player=player)
        print map(lambda m: (m.guess, m.bulls, m.cows), my_moves)
        number = ''
        rand = random.Random()
        for i in range(4):
            number += str(rand.randint(0, 9))
        return number
