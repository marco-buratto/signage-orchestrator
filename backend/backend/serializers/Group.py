from rest_framework import serializers


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=True)
    comment = serializers.CharField(max_length=255, required=False, allow_blank=True)

    players = serializers.JSONField(required=False) # @todo: PlayerSerializer().
