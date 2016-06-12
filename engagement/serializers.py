from rest_framework import serializers

from admin_custom.fields import UserPublicationUnicodeField
from engagement.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    member = UserPublicationUnicodeField(source='actor', read_only=True)

    class Meta:
        model = Comment
        fields = ('timestamp', 'publication_user', 'member')

# TODO: create Hyperlinked field
