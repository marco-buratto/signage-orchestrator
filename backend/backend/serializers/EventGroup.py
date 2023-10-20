from rest_framework import serializers


class EventGroupsSerializer(serializers.Serializer):
    class EventGroupInnerSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True)

    group = EventGroupInnerSerializer(required=True)
