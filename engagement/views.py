from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(write_up=self.get_object(), actor=request.user)
        return Response(serializer.data)


class CommentNestedView(ListAPIView):
    """"""

    serializer_class = CommentSerializer

    write_up = None
    reply_to = None

    def get_object(self):
        write_up_id = self.kwargs.get('write_up_id', None)
        if write_up_id:
            return get_object_or_404(WriteUp, id=write_up_id)
        else:
            raise SuspiciousOperation("No object found")

    def get_comment(self):
        comment_id = self.kwargs.get('comment_id', None)
        if comment_id:
            return get_object_or_404(Comment, id=comment_id)
        else:
            raise SuspiciousOperation("No object found")

    def get_queryset(self):
        self.validate()
        return Comment.objects.filter(write_up=self.write_up, reply_to=self.reply_to)

    def post(self, request, *args, **kwargs):
        self.validate()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(write_up=self.write_up, actor=request.user, reply_to=self.reply_to)
        return Response(serializer.data)

    def validate(self):
        self.write_up = self.get_object()
        self.reply_to = self.get_comment()
        if not self.write_up.comment_set.filter(pk=self.reply_to.pk).exists():
            raise SuspiciousOperation("No object found.")
