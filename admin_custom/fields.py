from rest_framework import serializers
from django.contrib.auth import get_user_model

from publication.models import Publication
from publication.serializers import PublicationSerializer
from user_custom.serializers import UserSerializer


class UserPublicationUnicodeField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Publication):
            return value.name
        elif isinstance(value, get_user_model()):
            return value.username
        raise Exception('Unexpected type of object')


class UserPublicationSerializedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Publication):
            serializer = PublicationSerializer(value)
        elif isinstance(value, get_user_model()):
            serializer = UserSerializer(value)
        else:
            raise Exception('Unexpected type of object')
        return serializer.data
