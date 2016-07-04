from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from admin_custom.fields import UserPublicationSerializedField
from engagement.models import Comment
from publication.models import Publication
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


class VoteSerializer(serializers.Serializer):
    vote_type = serializers.NullBooleanField()


class SubscriberSerializer(serializers.Serializer):
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
