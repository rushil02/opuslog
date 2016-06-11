from rest_framework import serializers
from django.contrib.auth import get_user_model

from publication.models import Publication
from publication.serializers import PublicationSerializer
from user_custom.serializers import UserSerializer


class UserPublicationUnicodeField(serializers.RelatedField):
    """ Used with Nested fields in GFK for USer/Publication, returns unicode """

    def to_representation(self, value):
        if isinstance(value, Publication):
            return value.name
        elif isinstance(value, get_user_model()):
            return value.username
        raise Exception('Unexpected type of object')


class UserPublicationSerializedField(serializers.RelatedField):
    """
    Used with Nested fields in GFK for USer/Publication, returns object
    Takes publication_serializer and user_serializer as arguments to set
    Nested Serializer
    """

    publication_serializer = None
    user_serializer = None

    def __init__(self, *args, **kwargs):
        self.publication_serializer = kwargs.pop('publication_serializer', PublicationSerializer)
        self.user_serializer = kwargs.pop('user_serializer', UserSerializer)

        super(UserPublicationSerializedField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if isinstance(value, Publication):
            serializer = self.publication_serializer(value)
        elif isinstance(value, get_user_model()):
            serializer = self.user_serializer(value)
        else:
            raise Exception('Unexpected type of object')
        return serializer.data
