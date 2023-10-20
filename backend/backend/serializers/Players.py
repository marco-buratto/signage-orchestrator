from rest_framework import serializers

from backend.serializers.Player import PlayerSerializer


class PlayersSerializer(serializers.Serializer):
    items = PlayerSerializer(many=True)
