from rest_framework import serializers

from admin_custom.fields import UserPublicationSerializedField
from engagement.models import Comment, VoteWriteUp
from publication.serializers import PublicationSerializerTwo
from user_custom.serializers import UserSerializerTwo


class CommentSerializer(serializers.ModelSerializer):
    member = UserPublicationSerializedField(source='actor', read_only=True,
                                            user_serializer=UserSerializerTwo,
                                            publication_serializer=PublicationSerializerTwo)

    class Meta:
        model = Comment
        fields = ('id', 'timestamp', 'member', 'comment_text', 'up_votes', 'down_votes', 'replies_num',
                  'delete_flag')
        read_only_fields = ('up_votes', 'down_votes', 'replies_num')


class VoteWriteUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteWriteUp
        read_only_fields = ('validation', 'content_type', 'object_id', 'write_up', 'vote_type')
