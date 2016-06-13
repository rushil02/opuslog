from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView

from engagement.models import Comment
from engagement.serializers import CommentSerializer
from write_up.models import WriteUp


class CommentFirstLevelView(ListAPIView):
    """"""

    serializer_class = CommentSerializer

    def get_object(self):
        write_up_id = self.kwargs.get('write_up_id', None)
        if write_up_id:
            return get_object_or_404(WriteUp, id=write_up_id)
        else:
            raise SuspiciousOperation("No object found")

    def get_queryset(self):
        return Comment.objects.filter(write_up=self.get_object(), reply_to=None)


class CommentSecondLevelView(ListAPIView):
    """"""

    serializer_class = CommentSerializer

    def get_object(self):
        write_up_id = self.kwargs.get('write_up_id', None)
        if write_up_id:
            return get_object_or_404(WriteUp, id=write_up_id)
        else:
            raise SuspiciousOperation("No object found")

    def get_comment(self):
        write_up_id = self.kwargs.get('comment_id', None)
        if write_up_id:
            return get_object_or_404(Comment, id=write_up_id)
        else:
            raise SuspiciousOperation("No object found")

    def get_queryset(self):
        return Comment.objects.filter(write_up=self.get_object(), reply_to=self.get_comment())
