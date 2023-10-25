from rest_framework import serializers

class PlaylistSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    playlist_type = serializers.CharField(max_length=16, required=True) # @todo: enum.
    name = serializers.CharField(max_length=255, required=True)

    url = serializers.CharField(max_length=2048, required=False, allow_blank=True)
    compatibility = serializers.BooleanField(required=False)
    pointer_disabled = serializers.BooleanField(required=False)
    reset_time_min = serializers.IntegerField(required=False)
    reload_time_s = serializers.IntegerField(required=False)

    mediaconf = serializers.CharField(max_length=65535, required=False, allow_blank=True)
    transition = serializers.IntegerField(required=False)
    blend = serializers.IntegerField(required=False)
