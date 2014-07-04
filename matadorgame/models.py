from django.db import models as M
from django.contrib.auth.models import User, Group
from zope.dottedname.resolve import resolve
from itertools import chain

"""
Models for the game ``Matador`` or Bulls & Cows with bots
"""

class Player(M.Model):
    """
    Can either be a User or a Bot
    """
    def get_games(self):
        return list(chain(self.games_as_first.all(),
                          self.games_as_second.all()))

    def get_next_move(self, game):
        return Move.objects.create(game=game)

class HumanPlayer(Player):
    """
    A human user of this application
    """
    user = M.OneToOneField(User)
    region = M.CharField(max_length=128)

class Bot(Player):
    name = M.CharField(
        max_length=128,
        unique=True,
        null=False,
        blank=False,
        help_text="Name for this bot player")

    description = M.TextField(
        null=False,
        blank=True,
        help_text="Implementation comments")

    implementation = M.CharField(
        max_length=512,
        unique=True,
        null=False,
        blank=False,
        help_text="Full dotted name of Bot subclass")

    def get_next_move(self, game):
        Bot_Class = resolve(self.implementation)
        bot_guess = Bot_Class().guess(game)
        return Move.objects.create(game=game,
                                   player=self,
                                   guess=bot_guess)

def valid_grade(value):
    return value >= 0 and value <= 4

class Game(M.Model):
    """
    An instance of a game
    """
    player1 = M.ForeignKey(
        Player,
        help_text="Player 1",
        related_name="games_as_first")

    player2 = M.ForeignKey(
        Player,
        help_text="Player 2",
        related_name="games_as_second")

    def get_opponent(self, player):
        if player == self.player1:
            return self.player2
        else:
            return self.player1

class Move(M.Model):
    game = M.ForeignKey(Game, related_name='moves')

    player = M.ForeignKey(Player, related_name='moves')

    guess = M.CharField(
        max_length=4,
        help_text="The guess of opponent's number",
        null=True)

    bulls = M.IntegerField(
        validators=[valid_grade],
        help_text="Count of correct numbers in incorrect spots",
        null=True)

    cows = M.IntegerField(
        validators=[valid_grade],
        help_text="Count of correct numbers in correct spots",
        null=True)

    def save(self, *args, **kwargs):
        if self.guess:
            print "Got a guess"
            self.bulls, self.cows = self._evaluate(self.guess)
        super(Move, self).save(*args, **kwargs)

    def _evaluate(self, guess):
        try:
            number = PlayerNumber.objects.get(
                player=self.game.get_opponent(self.player),
                game=self.game).number
            bulls = []
            cows  = []
            for spot in range(4):
                # 0, 1, 2, 3
                if guess[spot] == number[spot]:
                    cows.append(spot)
            for spot in range(4):
                if spot in cows:
                    # This digit is already a cow, skip
                    continue
                for subspot in range(4):
                    if subspot in cows or subspot in bulls:
                        continue
                    if guess[spot] == number[subspot]:
                        bulls.append(spot)
                        break

            print bulls, cows
            return (len(bulls), len(cows))
        except Exception as e:
            print e
            return (None, None)

class PlayerNumber(M.Model):
    game = M.ForeignKey(Game)
    player = M.ForeignKey(Player)
    number = M.CharField(max_length=4)

    class Meta:
        unique_together = ('game', 'player')
