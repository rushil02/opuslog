from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from admin_custom.fields import UserPublicationUnicodeField
from messaging_system.models import Thread, ThreadMembers, Message


class ThreadMembersSerializer(serializers.ModelSerializer):
    member = UserPublicationUnicodeField(source='entity', read_only=True)

    class Meta:
        model = ThreadMembers
        fields = ('member',)


class ThreadSerializer(serializers.ModelSerializer):
    members = SerializerMethodField()
    created_by = serializers.StringRelatedField(read_only=True)

    def get_members(self, thread):
        members_queryset = thread.threadmembers_set.all()
        serializer = ThreadMembersSerializer(instance=members_queryset, many=True)
        return serializer.data

    class Meta:
        model = Thread
        fields = ('id', 'subject', 'created_by', 'create_time', 'members',)


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        exclude = ('thread', 'id')
