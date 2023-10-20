from rest_framework import serializers

class PlaylistSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    playlist_type = serializers.CharField(max_length=16, required=True) # @todo: enum.
    name = serializers.CharField(max_length=255, required=True)
    mediaconf = serializers.CharField(max_length=65535, required=False, allow_blank=True)
    transition = serializers.IntegerField(required=False)
    blend = serializers.IntegerField(required=False)
