from rest_framework import serializers

from backend.serializers.Event import EventSerializer


class EventsSerializer(serializers.Serializer):
    items = EventSerializer(many=True)
