from matadorgame.models import Game, Player
from django import template

register = template.Library()

@register.simple_tag
def opponent(game, me):
    return game.get_opponent(me).name

@register.simple_tag
def status(game, me):
    return game.get_status(me)
