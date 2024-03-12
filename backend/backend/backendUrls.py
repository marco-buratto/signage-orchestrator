from django.urls import path

from backend.controllers import Root
from backend.controllers.orchestrator import Group, EventGroups, Playlist, Playlists, Players, Event, EventPlaylist, \
    Groups, GroupPlayers, Player, Events, GroupPlayer, EventPlaylists

urlpatterns = [
    path('', Root.RootController.as_view()),

    path('group/<int:groupId>/', Group.GroupController.as_view(), name='group'),
    path('groups/', Groups.GroupsController.as_view(), name='groups'),

    path('player/<int:playerId>/', Player.PlayerController.as_view(), name='player'),
    path('players/', Players.PlayersController.as_view(), name='players'),

    path('group/<int:groupId>/player/<int:playerId>/', GroupPlayer.GroupPlayerController.as_view(), name='group-player'),
    path('group/<int:groupId>/players/', GroupPlayers.GroupPlayersController.as_view(), name='group-players'),

    path('playlist/<int:playlistId>/', Playlist.PlaylistController.as_view(), name='playlist'),
    path('playlists/', Playlists.PlaylistsController.as_view(), name='playlists'),

    path('event/<int:eventId>/', Event.EventController.as_view(), name='event'),
    path('events/', Events.EventsController.as_view(), name='events'),

    path('event/<int:eventId>/groups/', EventGroups.EventGroupsController.as_view(), name='event-groups'),

    path('event/<int:eventId>/playlist/<int:playlistId>/', EventPlaylist.EventPlaylistController.as_view(), name='event-playlist'),
    path('event/<int:eventId>/playlists/', EventPlaylists.EventPlaylistsController.as_view(), name='event-playlists'),
]
