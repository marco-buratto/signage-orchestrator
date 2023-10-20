from rest_framework import serializers


class GroupPlayerSerializer(serializers.Serializer):
    class GroupPlayerInnerSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True)

    player = GroupPlayerInnerSerializer(required=True)
