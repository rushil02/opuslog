from rest_framework import serializers

from admin_custom.fields import UserPublicationUnicodeField
from engagement.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    member = UserPublicationUnicodeField(source='actor', read_only=True)
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='user_custom:user',
    #     lookup_field='write_up'
    # )

    class Meta:
        model = Comment
        fields = ('timestamp', 'member', 'url')
