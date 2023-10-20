from rest_framework import serializers

from backend.serializers.Group import GroupSerializer


class GroupsSerializer(serializers.Serializer):
    items = GroupSerializer(many=True)
