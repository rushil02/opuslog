from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from admin_custom.fields import UserPublicationUnicodeField
from messaging_system.models import Thread, ThreadMembers, Message
from publication.models import Publication


class ThreadMembersSerializer(serializers.ModelSerializer):
    member = UserPublicationUnicodeField(source='entity', read_only=True)
    content_type = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ThreadMembers
        fields = ('member', 'content_type')


class AddMemberSerializer(serializers.Serializer):
    entity_handler = serializers.CharField(max_length=30)
    obj = None

    def validate(self, attrs):
        handler = attrs.get('entity_handler')

        try:
            self.obj = get_user_model().objects.get(username=handler)
        except ObjectDoesNotExist:
            try:
                self.obj = Publication.objects.get(handler=handler)
            except ObjectDoesNotExist:
                raise ValidationError("Object does not exist")
            else:
                return attrs
        else:
            return attrs


class ThreadSerializer(serializers.ModelSerializer):
    members = SerializerMethodField()
    created_by = serializers.StringRelatedField(read_only=True)

    def get_members(self, thread):
        members_queryset = thread.threadmembers_set.all()
        serializer = ThreadMembersSerializer(instance=members_queryset, many=True)
        return serializer.data

    class Meta:
        model = Thread
        fields = ('id', 'subject', 'created_by', 'create_time', 'members')


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        exclude = ('thread', 'id')
        read_only_fields = ('read_at', 'sender')
