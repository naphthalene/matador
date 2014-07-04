from random import Random
from itertools import chain
from django.db import models as M
from model_utils.managers import InheritanceManager
from zope.dottedname.resolve import resolve
from django.contrib.auth.models import User, Group

"""
Models for the game ``Matador`` or Bulls & Cows with bots
"""

class Player(M.Model):
    name = M.CharField(
        max_length=128,
        unique=True,
        null=False,
        blank=False,
        help_text="Name for this bot player")

    objects = InheritanceManager()
    """
    Can either be a User or a Bot
    """
    def get_games(self):
        return list(chain(self.games_as_first.all(),
                          self.games_as_second.all()))

    def get_next_move(self, game):
        pass

class HumanPlayer(Player):
    """
    A human user of this application
    """
    user = M.OneToOneField(User)
    region = M.CharField(max_length=128)

    def get_next_move(self, game):
        ## TODO email user and update any active page
        pass

class Bot(Player):
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
        bot_guess = resolve(self.implementation)().guess(game)
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
        if player.id == self.player1.id:
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
            self.bulls, self.cows = self._evaluate(self.guess)
        super(Move, self).save(*args, **kwargs)

    def _evaluate(self, guess):
        try:
            number = PlayerNumber.objects.get(
                player=self.game.get_opponent(self.player),
                game=self.game).number
            print "Player %s made guess of %s where real number is %s" \
                % (self.player.name, guess, number)
            bulls = []
            cows  = []
            for spot in range(4):
                if guess[spot] == number[spot]:
                    cows.append(spot)

            guessed_spots = cows[:]
            for spot in range(4):
                if spot in cows:
                    # This digit is already a cow, skip
                    continue
                for subspot in range(4):
                    # If the digit in the ``number`` has already been
                    # claimed by another digit in the guess
                    if subspot in guessed_spots:
                        continue
                    if guess[spot] == number[subspot]:
                        bulls.append(spot)
                        guessed_spots.append(subspot)
                        break

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
