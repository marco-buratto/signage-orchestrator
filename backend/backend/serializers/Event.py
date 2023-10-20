from rest_framework import serializers

class EventSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=16, required=True)
    start_date = serializers.CharField(max_length=16, required=True)
    end_date = serializers.CharField(max_length=16, required=True)
    text = serializers.CharField(max_length=65535, required=False, allow_blank=True)

    group = serializers.JSONField(required=False) # @todo: GroupSerializer().
    playlist = serializers.JSONField(required=False) # @todo: PlaylistSerializer().
