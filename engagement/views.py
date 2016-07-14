from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from custom_package.mixins import AbstractMixin
from engagement.models import Comment, VoteWriteUp, Subscriber, VoteComment
from engagement.serializers import CommentSerializer, VoteSerializer, SubscriberSerializer
from write_up.models import WriteUp


class CommentFirstLevelView(AbstractMixin, ListAPIView):
    """ get or create first level comments """

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
        self.notify_single(user=self.write_up.get_owner().contributor, notification_type='CO', acted_on=self.write_up)
        if self.reply_to:
            self.notify_single(notify_self_pub=False, user=self.reply_to.actor, notification_type='CR',
                               acted_on=self.write_up, )
        obj.process_comment_async(actor_handler=self.get_actor_handler())
        self.log(request, obj, args, kwargs, 'comment', 'engagement.views.CommentFirstLevelView/CommentNestedView.post')
        return Response(serializer.data)

    def validate(self):
        self.write_up = self.get_object()


class CommentNestedView(CommentFirstLevelView):
    """ get or create second level comments """

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


class DeleteCommentView(AbstractMixin, GenericAPIView):
    """ delete any level comment """

    serializer_class = CommentSerializer

    write_up = None
    comment = None

    def get_comment(self):
        raise NotImplementedError("Implement in Subclass")

    def get_object(self):
        write_up_uuid = self.kwargs.get('write_up_uuid', None)
        if write_up_uuid:
            return get_object_or_404(WriteUp, uuid=write_up_uuid)
        else:
            raise SuspiciousOperation("No object found")

    def validate(self):
        self.write_up = self.get_object()
        self.comment = self.get_comment()
        if not self.write_up.comment_set.filter(pk=self.comment.pk).exists():
            raise SuspiciousOperation("No object found.")

    def delete(self, request, *args, **kwargs):
        self.validate()
        self.comment.delete_flag = True
        self.comment.save()
        serializer = self.get_serializer(self.comment)
        self.log(request, self.comment, args, kwargs, 'delete_comment', 'engagement.views.DeleteCommentView.delete')
        return Response(serializer.data)


class VoteWriteupView(AbstractMixin, GenericAPIView):
    serializer_class = VoteSerializer
    write_up = None

    def get_object(self):
        write_up_uuid = self.kwargs.get('write_up_uuid', None)
        if write_up_uuid:
            return get_object_or_404(WriteUp, uuid=write_up_uuid)
        else:
            raise SuspiciousOperation("No object found")

    def post(self, request, *args, **kwargs):
        self.write_up = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data.get('vote_type', None)

        obj, created = VoteWriteUp.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.get_actor()),
            object_id=self.get_actor().id, write_up=self.write_up)

        changed = False
        if obj.vote_type != vote_type:
            changed = True
            obj.vote_type = vote_type
            obj.save()

        if changed or created:
            if vote_type:
                notification_type = 'UW'
            else:
                notification_type = 'DW'
            self.notify_single(user=self.write_up.get_owner().contributor, notification_type=notification_type,
                               acted_on=self.write_up, )
        self.log(request, obj, args, kwargs, 'vote_write_up', 'engagement.views.VoteWriteupView.post')
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        self.write_up = self.get_object()

        try:
            obj = VoteWriteUp.objects.get(
                content_type=ContentType.objects.get_for_model(self.get_actor()),
                object_id=self.get_actor().id, write_up=self.write_up
            )
        except VoteWriteUp.DoesNotExist:
            return Response(status=status.HTTP_200_OK)
        else:
            obj.vote_type = None
            obj.save()
            self.log(request, obj, args, kwargs, 'remove_vote_write_up', 'engagement.views.VoteWriteupView.delete')
            return Response(status=status.HTTP_200_OK)


class SubscriberView(AbstractMixin, GenericAPIView):
    serializer_class = SubscriberSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscribed = serializer.obj

        obj, created = Subscriber.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(self.get_actor()),
            object_id=self.get_actor().id, content_type_2=ContentType.objects.get_for_model(subscribed),
            object_id_2=subscribed.id, defaults={'unsubscribe_flag': True}
        )

        if created:
            self.notify_single(user=obj.subscribed, notification_type='SU', acted_on=obj.subscribed,
                               suffix=obj.content_type_2.model)
        self.log(request, obj, args, kwargs, 'subscribe', 'engagement.views.SubscriberView.post')
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscribed = serializer.obj

        obj, created = Subscriber.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(self.get_actor()),
            object_id=self.get_actor().id, content_type_2=ContentType.objects.get_for_model(subscribed),
            object_id_2=subscribed.id, defaults={'unsubscribe_flag': False}
        )

        self.notify_single(user=obj.subscribed, notification_type='US', acted_on=obj.subscribed,
                           suffix=obj.content_type_2.model)
        self.log(request, obj, args, kwargs, 'unsubscribe', 'engagement.views.SubscriberView.delete')
        return Response(status=status.HTTP_200_OK)


class VoteCommentView(AbstractMixin, GenericAPIView):
    serializer_class = VoteSerializer
    comment = None

    def get_object(self):
        comment_id = self.kwargs.get('comment_id', None)
        if comment_id:
            return get_object_or_404(Comment, id=comment_id)
        else:
            raise SuspiciousOperation("No object found")

    def post(self, request, *args, **kwargs):
        self.comment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data.get('vote_type', None)

        obj, created = VoteComment.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.get_actor()),
            object_id=self.get_actor().id, comment=self.comment,
        )

        changed = False
        if obj.vote_type != vote_type:
            changed = True
            obj.vote_type = vote_type
            obj.save()

        if changed or created:
            if vote_type:
                notification_type = 'UC'
            else:
                notification_type = 'DC'
            self.notify_single(user=self.comment.actor, notification_type=notification_type, acted_on=self.comment,
                               write_up=self.comment.write_up)
        self.log(request, obj, args, kwargs, 'vote_comment', 'engagement.views.VoteCommentView.post')
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        self.comment = self.get_object()

        try:
            obj = VoteComment.objects.get(
                content_type=ContentType.objects.get_for_model(self.get_actor()),
                object_id=self.get_actor().id, comment=self.comment
            )
        except VoteComment.DoesNotExist:
            return Response(status=status.HTTP_200_OK)
        else:
            obj.vote_type = None
            obj.save()
            self.log(request, obj, args, kwargs, 'remove_vote_comment', 'engagement.views.VoteCommentView.delete')
            return Response(status=status.HTTP_200_OK)
