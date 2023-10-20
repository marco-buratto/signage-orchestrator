from rest_framework import serializers

from backend.serializers.Playlist import PlaylistSerializer


class PlaylistsSerializer(serializers.Serializer):
    items = PlaylistSerializer(many=True)
