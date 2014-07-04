from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from matadorgame.models import HumanPlayer, Game, Move

## TODO route
def login_view(request):
    login_context     = {}
    # ----------------------------------------------------------
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            redirect('dashboard_view', permanent=True)
        else:
            pass
    else:
        redirect('login_view')

## TODO route
def logout_view(request):
    logout(request)

@login_required
def dashboard_view(request):
    dash_template = 'dashboard.html'
    dash_context  = {}
    # ----------------------------------------------------------
    player = HumanPlayer(user=request.user)
    dash_context['my_games'] = player.get_games()
    render(request, dash_template, context=dash_context)
