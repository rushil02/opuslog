from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from engagement.models import Comment, VoteWriteUp, Subscriber
from engagement.serializers import CommentSerializer, VoteWriteUpSerializer, SubscriberSerializer
from essential.tasks import notify_async
from write_up.models import WriteUp


class Mixin(object):
    def get_actor(self):
        raise NotImplementedError("Override in subclass")

    def get_actor_for_activity(self):
        raise NotImplementedError("Override in subclass")

    def get_actor_handler(self):
        raise NotImplementedError("Override in subclass")


class CommentFirstLevelView(Mixin, ListAPIView):
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
        owner = self.write_up.get_owner()
        notify_async.delay(
            user_object_id=owner.object_id,
            user_content_type=owner.content_type.id,
            notification_type='CO',
            write_up_id=self.write_up.id,
            redirect_url="bcbc",
            actor_handler=self.get_actor_handler()
        )
        obj.process_comment_async(actor_handler=self.get_actor_handler())
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


class DeleteCommentView(CommentNestedView):
    """ delete any level comment """

    def delete(self, request, *args, **kwargs):
        self.validate()
        comment = self.reply_to
        comment.delete_flag = True
        comment.save()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)


class VoteWriteupView(Mixin, GenericAPIView):
    serializer_class = VoteWriteUpSerializer
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

        obj, created = VoteWriteUp.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(self.get_actor()),
            object_id=self.get_actor().id, write_up=self.write_up,
            defaults={'vote_type': vote_type}
        )

        owner = self.write_up.get_owner()
        if created:
            notify_async.delay(
                user_object_id=owner.object_id,
                user_content_type=owner.content_type.id,
                notification_type='CO',
                write_up_id=self.write_up.id,
                redirect_url="bcbc",
                actor_handler=self.get_actor_handler()
            )
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
        except Exception as e:
            pass  # TODO: activitylog
        else:
            obj.vote_type = None
            obj.save()
            return Response(status=status.HTTP_200_OK)


class SubscriberView(Mixin, GenericAPIView):
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

        # if created:  # TODO: create notification
        #     notify_async.delay(
        #         user_object_id=owner.object_id,
        #         user_content_type=owner.content_type.id,
        #         notification_type='CO',
        #         redirect_url="bcbc",
        #         actor_handler=self.get_actor_handler()
        #     )
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

        # if created:
        #     notify_async.delay(
        #         user_object_id=owner.object_id,
        #         user_content_type=owner.content_type.id,
        #         notification_type='CO',
        #         redirect_url="bcbc",
        #         actor_handler=self.get_actor_handler()
        #     )
        return Response(status=status.HTTP_200_OK)
