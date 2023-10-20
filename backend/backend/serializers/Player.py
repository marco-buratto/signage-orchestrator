from rest_framework import serializers

class PlayerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    uuid = serializers.CharField(max_length=64, required=True)
    player_type = serializers.CharField(max_length=16, required=True) # @todo: enum.
    name = serializers.CharField(max_length=255, required=True)
    position = serializers.CharField(max_length=255, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=True)
    comment = serializers.CharField(max_length=255, required=False, allow_blank=True)
    metrics = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ssh_public_key = serializers.CharField(max_length=2048, required=False, allow_blank=True)

    group = serializers.JSONField(required=False) # @todo: GroupSerializer().
