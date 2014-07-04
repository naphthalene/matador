from django.http import HttpResponse
from django.shortcuts import render, redirect
from matadorgame.models import HumanPlayer, Game, Move, PlayerNumber, Player
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    dash_template = 'matadorgame/dashboard.html'
    dash_context  = {}
    # ----------------------------------------------------------
    # Implementation
    player = HumanPlayer.objects.get(user=request.user)
    dash_context['me'] = player
    dash_context['my_games'] = player.get_games()
    print dash_context['me']
    return render(request, dash_template, dash_context)

@login_required
def game(request, game_id):
    game_template = 'matadorgame/game.html'
    game_context  = {}
    # ----------------------------------------------------------
    # Implementation
    game = Game.objects.get(id=game_id)
    player = HumanPlayer.objects.get(user=request.user)
    my_number = PlayerNumber.objects.get(game=game, player=player).number
    game_context['me'] = player
    game_context['game'] = game
    game_context['my_num'] = my_number
    game_context['my_moves'] \
        = game.moves.filter(player=player)
    game_context['opponent_moves'] \
        = game.moves.filter(player=game.get_opponent(player))
    return render(request, game_template, game_context)

@csrf_exempt
@require_POST
def guess(request):
    # ----------------------------------------------------------
    # Implementation
    player = HumanPlayer.objects.get(user=request.user)
    game_id   = request.POST['game_id']
    guess_val = request.POST['value']

    try:
        Move.objects.create(game_id=game_id,
                            player=player,
                            guess=guess_val)

        # Request a move from the other player or bot
        game = Game.objects.get(id=int(game_id))
        opponent = game.get_opponent(player)
        op_class = Player.objects.get_subclass(id=opponent.id)
        op_class.get_next_move(game)
        return redirect('matadorgame.views.game', game_id)

    except Exception as e:
        hresp = HttpResponse(e.__str__())
        hresp.status_code=400
        return hresp
