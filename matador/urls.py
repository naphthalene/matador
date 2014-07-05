from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'matadorgame.views.dashboard_view',
        name='dashboard'),
    url(r'^games/(?P<game_id>\d+)', 'matadorgame.views.game'),
    url(r'^guess/$', 'matadorgame.views.guess'),
    url(r'^player_suggest/$', 'matadorgame.views.player_suggest'),
    url(r'^new_game/$', 'matadorgame.views.new_game'),
    url(r'^accept_game/$', 'matadorgame.views.accept_game'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^accounts/login/$',  'django.contrib.auth.views.login',
        { 'template_name': 'matadorgame/login.html' }),
    url(r'^accounts/create/$', 'matadorgame.views.create_account'),
    url(r'^admin/', include(admin.site.urls)),
)
