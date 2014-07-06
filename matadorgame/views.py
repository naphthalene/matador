from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from matadorgame.models import HumanPlayer, Game, Move, PlayerNumber, Player
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User, Group
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
    dash_context['my_games'] = sorted(player.get_games(),
                                      key=lambda g: g.id,
                                      reverse=True)
    dash_context['invites'] = sorted(player.get_invitations(),
                                     key=lambda g: g.id,
                                     reverse=True)
    return render(request, dash_template, dash_context)

@login_required
def game(request, game_id):
    game_template = 'matadorgame/game.html'
    game_context  = {}
    # ----------------------------------------------------------
    # Implementation
    game = Game.objects.get(id=game_id)
    player = HumanPlayer.objects.get(user=request.user)

    # Check that the opponent has created a number for this game (accepted)
    opponent = game.get_opponent(player)
    try:
        opponent_number =PlayerNumber.objects.get(game=game, player=opponent)
        my_number = PlayerNumber.objects.get(game=game, player=player).number
        game_context['me'] = player
        game_context['game'] = game
        game_context['my_num'] = my_number
        game_context['my_moves'] \
            = game.moves.filter(player=player)
        game_context['opponent_moves'] \
            = game.moves.filter(player=game.get_opponent(player))
        return render(request, game_template, game_context)
    except:
        # Means the opponent hasn't accepted the invitation yet
        return redirect('matadorgame.views.dashboard_view')

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

@csrf_exempt
@require_POST
def accept_game(request):
    # ----------------------------------------------------------
    # Implementation
    player = HumanPlayer.objects.get(user=request.user)
    number = request.POST['number']
    game_id = int(request.POST['game_id'])
    game = Game.objects.get(id=game_id)
    PlayerNumber.objects.create(game=game, player=player, number=number)
    return redirect('matadorgame.views.game', game_id)

@csrf_exempt
@require_POST
def new_game(request):
    # ----------------------------------------------------------
    # Implementation
    player = HumanPlayer.objects.get(user=request.user)

    opponent_id = request.POST['opponent'][1:-1]
    opponent = Player.objects.get_subclass(id=opponent_id)

    game = Game.objects.create(player1=player, player2=opponent)

    my_number = request.POST['number']
    PlayerNumber.objects.create(game=game, player=player, number=my_number)

    opponent.request_secret_number(game)

    return redirect('matadorgame.views.game', game.id)


@csrf_exempt
@require_POST
def player_suggest(request):
    player = HumanPlayer.objects.get(user=request.user)
    query = request.REQUEST['query']
    json_list = Player.get_suggestions(query, exclude_id=player.id)
    return HttpResponse(json_list, content_type='application/json')

@csrf_exempt
@require_POST
def create_account(request):
    username         = request.POST['username']
    email            = request.POST['email']
    password         = request.POST['password']
    full_name        = request.POST['full_name']
    password_confirm = request.POST['password_confirm']
    if password != password_confirm or\
       User.objects.filter(username=username).exists():
        return redirect('django.contrib.auth.views.login')
    split_name = full_name.split(' ')
    user = User.objects.create_user(username,
                                    email,
                                    password,
                                    first_name = split_name[0])

    HumanPlayer.objects.create(user=user, name=full_name)

    return redirect('matadorgame.views.dashboard_view')
