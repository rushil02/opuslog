from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from admin_custom.fields import UserPublicationSerializedField, UserPublicationUnicodeField
from messaging_system.models import Thread, ThreadMember, Message
from publication.models import Publication
from publication.serializers import PublicationSerializerTwo
from user_custom.serializers import UserSerializerTwo


class ThreadMemberSerializer(serializers.ModelSerializer):
    """ Serializes ThreadMember model """

    member = UserPublicationSerializedField(source='entity', read_only=True,
                                            user_serializer=UserSerializerTwo,
                                            publication_serializer=PublicationSerializerTwo)
    content_type = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ThreadMember
        fields = ('content_type', 'member', 'removed')


class AddMemberSerializer(serializers.Serializer):
    """ Custom Serializer to add/delete members """

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop('thread', None)
        super(AddMemberSerializer, self).__init__(*args, **kwargs)

    entity_handler = serializers.CharField(max_length=30)
    obj = None

    def validate_entity_handler(self, value):
        handler = value

        try:
            self.obj = get_user_model().objects.get(username=handler)
        except ObjectDoesNotExist:
            try:
                self.obj = Publication.objects.get(handler=handler)
            except ObjectDoesNotExist:
                raise ValidationError("Object does not exist")
            else:
                if self.thread.threadmember_set.filter(publication=self.obj).exists():
                    raise ValidationError("Member already exists")
        else:
            if self.thread.threadmember_set.filter(user=self.obj).exists():
                raise ValidationError("Member already exists")
        return value


class ThreadSerializer(serializers.ModelSerializer):
    """ Serializes Thread model """

    members = SerializerMethodField(read_only=True)
    created_by = UserPublicationUnicodeField(read_only=True)

    def get_members(self, thread):
        members_queryset = thread.threadmember_set.all().prefetch_related('entity')
        serializer = ThreadMemberSerializer(instance=members_queryset, many=True)
        return serializer.data

    class Meta:
        model = Thread
        fields = ('id', 'subject', 'created_by', 'create_time', 'members')


class MessageSerializer(serializers.ModelSerializer):
    """ Serializes Message model """

    class Meta:
        model = Message
        exclude = ('thread', 'id')
        read_only_fields = ('read_at', 'sender')
