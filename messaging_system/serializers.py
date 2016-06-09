from django.contrib.auth import get_user_model
from rest_framework import serializers

from messaging_system.models import Thread
from publication.models import Publication


class ThreadMembersField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Publication):
            return value.name
        elif isinstance(value, get_user_model()):
            return value.username
        raise Exception('Unexpected type of object')


class ThreadSerializer(serializers.ModelSerializer):
    members = ThreadMembersField(many=True)

    class Meta:
        model = Thread
        fields = ('subject', 'created_by', 'create_time', 'members')


class MessageSerializer(serializers.ModelSerializer):
    pass


class GetAllMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
