import json
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

    def get_invitations(self):
        def unaccepted_games(game):
            return not PlayerNumber.objects.filter(game=game,
                                                   player=self).exists()
        return filter(unaccepted_games, self.get_games())

    def get_next_move(self, game):
        pass

    def request_secret_number(self, game):
        number = ''
        rand = Random()
        for i in range(4):
            number += str(rand.randint(0, 9))
        return PlayerNumber.objects.create(game=game,
                                           player=self,
                                           number=number)

    @staticmethod
    def get_suggestions(query, exclude_id=None):
        if exclude_id:
            players = Player.objects.exclude(id=exclude_id)\
                                    .filter(name__icontains=query)
        else:
            players = Player.objects.all()\
                                    .filter(name__icontains=query)

        player_zip = map(lambda p: (p.id, p.name), players)
        return json.dumps(
            [{ "id": p[0], "name": p[1] } for p in player_zip]
        )

class HumanPlayer(Player):
    """
    A human user of this application
    """
    user = M.OneToOneField(User)
    region = M.CharField(max_length=128)

    def get_next_move(self, game):
        ## TODO email user and update any active page
        pass

    def request_secret_number(self, game):
        ## TODO email user to finish initalizing the game
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
        bot_guess = resolve(self.implementation)().guess(self, game)
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

    def get_status(self, player):
        # Possible statuses:
        # 1) Pending
        # 2) Active
        # 3) Won
        # 4) Lost
        opponent = self.get_opponent(player)
        try:
             PlayerNumber.objects.get(game=self, player=opponent)
        except:
            # The other player hasn't made come up with a number
            # yet. Game is pending
            return "Pending"

        player_moves   = self.moves.filter(player=player)
        opponent_moves = self.moves.filter(player=opponent)
        player_guessed_right   = player_moves.filter(bulls=4).exists()
        opponent_guessed_right = opponent_moves.filter(bulls=4).exists()

        if player_guessed_right and opponent_guessed_right:
            if len(player_moves) <= len(opponent_moves):
                return "Won"
            else:
                return "Lost"
        elif player_guessed_right and \
             len(opponent_moves) >= len(player_moves):
            return "Won"
        elif opponent_guessed_right and \
             len(opponent_moves) < len(player_moves):
            return "Lost"
        else:
            return "Active"

class Move(M.Model):
    game = M.ForeignKey(Game, related_name='moves')

    player = M.ForeignKey(Player, related_name='moves')

    guess = M.CharField(
        max_length=4,
        help_text="The guess of opponent's number",
        null=True)

    cows = M.IntegerField(
        validators=[valid_grade],
        help_text="Count of correct numbers in incorrect spots",
        null=True)

    bulls = M.IntegerField(
        validators=[valid_grade],
        help_text="Count of correct numbers in correct spots",
        null=True)

    def save(self, *args, **kwargs):
        if self.guess:
            self.cows, self.bulls = self._evaluate(self.guess)
        super(Move, self).save(*args, **kwargs)

    def _evaluate(self, guess):
        try:
            number = PlayerNumber.objects.get(
                player=self.game.get_opponent(self.player),
                game=self.game).number
            bulls = []
            cows  = []
            for spot in range(4):
                if guess[spot] == number[spot]:
                    bulls.append(spot)

            guessed_spots = bulls[:]
            for spot in range(4):
                if spot in bulls:
                    # This digit is already a cow, skip
                    continue
                for subspot in range(4):
                    # If the digit in the ``number`` has already been
                    # claimed by another digit in the guess
                    if subspot in guessed_spots:
                        continue
                    if guess[spot] == number[subspot]:
                        cows.append(spot)
                        guessed_spots.append(subspot)
                        break

            return (len(cows), len(bulls))
        except Exception as e:
            print e
            return (None, None)

class PlayerNumber(M.Model):
    game = M.ForeignKey(Game)
    player = M.ForeignKey(Player)
    number = M.CharField(max_length=4)

    class Meta:
        unique_together = ('game', 'player')
