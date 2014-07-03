from django.db import models
from django.contrib.auth.models import User, Group

"""
Models for the game ``Matador`` or Bulls & Cows with bots
"""

class Player(models.Model):
    """
    Can either be a user or a Bot
    """
    def get_games(self):
        raise Exception('Not implemented')

    def get_next_move(self, game):
        raise Exception('Not implemented')

    def get_last_move(self, game):
        raise Exception('Not implemented')

    class Meta:
        abstract = True

class HumanPlayer(Player):
    """
    A human user of this application
    """
    user = models.OneToOneField(User)
    region = models.CharField(max_length=128)

class Bot(Player):
    name = models.CharField(
        max_length=128,
        unique=True,
        null=False,
        blank=False,
        help_text="Name for this bot player")

    description = models.TextField(
        null=False,
        blank=True,
        help_text="Implementation details or comments")


def valid_guess(value):
    return isinstance(value, int) and value.length == 4

class Game(models.Model):
    """
    An instance of a game
    """
    player1 = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        help_text="Player 1")

    player2 = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        help_text="Player 2")

    player1number = models.IntegerField(validator=[valid_guess])
    player2number = models.IntegerFIeld(validator=[valid_guess])

    def get_moves(self):
        raise Exception('Not implemented')

class Move(models.Model):
    game = models.ForeignKey(Game, related_name='move')
    guess = models.IntegerField(validators=[valid_guess])
    bulls = models.IntegerField(validators=[lambda b: b <= 4])
    cows  = models.IntegerField(validators=[lambda b: b <= 4])
