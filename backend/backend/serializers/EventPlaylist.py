from rest_framework import serializers


class EventPlaylistsSerializer(serializers.Serializer):
    class EventPlaylistInnerSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True)

    playlist = EventPlaylistInnerSerializer(required=True)
