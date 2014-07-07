from base import Bot

class PrimeBot(Bot):
    def guess(self, player, game):
        my_moves = list(game.moves.filter(player=player))
        number = ''
        def previous_move():
            return my_moves[-1]

        if len(my_moves) == 0:
            # Initial guess
            number = '1234'

        elif len(my_moves) == 1:
            m = previous_move()
            if m.bulls > 0:
                # We already guessed 1 or more correct digits.
                number = m.guess[:m.bulls]
                remaining = 4 - m.bulls
                next_digit = 5
                for n in range(remaining):
                    number += (str(next_digit))
                    next_digit += 1
        else:
            number = '0000'
        return number
