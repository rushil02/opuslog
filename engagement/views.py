import abc

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

    reply_to = None
    write_up = None

    def get_object(self):
        write_up_uuid = self.kwargs.get('write_up_uuid', None)
        if write_up_uuid:
            return get_object_or_404(WriteUp, uuid=write_up_uuid)
        else:
            raise SuspiciousOperation("No object found")

    def get_queryset(self):
        self.validate()
        return Comment.objects.filter(write_up=self.write_up, reply_to=self.reply_to)

    def post(self, request, *args, **kwargs):
        self.validate()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(write_up=self.write_up, actor=self.get_actor(), reply_to=self.reply_to)
        obj.process_comment_async()
        return Response(serializer.data)

    @abc.abstractmethod
    def get_actor(self):
        raise NotImplementedError("Override in subclass")

    def validate(self):
        self.write_up = self.get_object()


class CommentNestedView(CommentFirstLevelView):
    """"""

    def get_comment(self):
        comment_id = self.kwargs.get('comment_id', None)
        if comment_id:
            return get_object_or_404(Comment, id=comment_id)
        else:
            raise SuspiciousOperation("No object found")

    def validate(self):
        self.write_up = self.get_object()
        self.reply_to = self.get_comment()
        if not self.write_up.comment_set.filter(pk=self.reply_to.pk).exists():
            raise SuspiciousOperation("No object found.")

    def delete(self, request, *args, **kwargs):
        self.validate()
        comment = self.reply_to
        comment.delete_request = True
        comment.save()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)

# class DeleteComment