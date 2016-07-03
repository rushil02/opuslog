from django.core.exceptions import SuspiciousOperation
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from admin_custom.models import ActivityLog
from messaging_system.models import Message, ThreadMember
from messaging_system.serializers import ThreadSerializer, MessageSerializer, AddMemberSerializer


class Mixin(object):
    def get_actor(self):
        raise NotImplementedError("Override in subclass")

    def get_thread_query(self, thread_id):
        raise NotImplementedError("Override in subclass")

    def get_actor_for_activity(self):
        raise NotImplementedError("Override in subclass")


class ThreadView(Mixin, ListAPIView):
    """
    Return list of threads of a user, creates a new entry and updates a given
    thread's subject.
    """

    serializer_class = ThreadSerializer

    def post(self, request, *args, **kwargs):
        """ Create new Thread and assign thread creator as thread member """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user)
        obj.threadmember_set.create(entity=self.get_actor())
        ActivityLog.objects.create_log(
            request, actor=self.get_actor_for_activity(), entity=obj, view='ThreadView',
            arguments={'args': args, 'kwargs': kwargs}, act_type='create_thread'
        )
        return Response(serializer.data)

    def get_object(self):
        thread_id = self.kwargs.get('thread_id', None)
        if thread_id:
            obj = self.get_thread_query(thread_id)
            return obj
        else:
            raise SuspiciousOperation("No object found")

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        ActivityLog.objects.create_log(
            request, actor=self.get_actor_for_activity(), entity=obj, view='ThreadView',
            arguments={'args': args, 'kwargs': kwargs}, act_type='update_thread_subject'
        )
        return Response(serializer.data)


class AddDeleteMemberView(Mixin, GenericAPIView):
    """ Add/Delete a member for a thread. """

    serializer_class = AddMemberSerializer

    def get_queryset(self):
        return ThreadMember.objects.all()

    def get_object(self):
        thread_id = self.kwargs.get('thread_id', None)
        if thread_id:
            obj = self.get_thread_query(thread_id)
            return obj
        else:
            raise SuspiciousOperation("No object found")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = ThreadMember.objects.create(thread=self.get_object(), entity=serializer.obj)
        except Exception as e:
            raise ValidationError(e.message)
        else:
            ActivityLog.objects.create_log(
                request, actor=self.get_actor_for_activity(), entity=obj, view='AddDeleteMemberView',
                arguments={'args': args, 'kwargs': kwargs}, act_type='add_member'
            )
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = ThreadMember.objects.get(thread=self.get_object(), entity=serializer.obj).update(removed=True)
        except Exception as e:
            raise ValidationError(e.message)
        else:
            ActivityLog.objects.create_log(
                request, actor=self.get_actor_for_activity(), entity=obj, view='AddDeleteMemberView',
                arguments={'args': args, 'kwargs': kwargs}, act_type='delete_member'
            )
        return Response(serializer.data)


class MessageView(Mixin, ListAPIView):
    """ Add and List messages. """

    serializer_class = MessageSerializer

    thread_obj = None

    def get_queryset(self):
        return Message.objects.filter(thread=self.kwargs.get('thread_id'))

    def set_user(self):
        raise NotImplementedError("Override in subclass")

    def get_object(self):
        thread_id = self.kwargs.get('thread_id', None)
        if thread_id:
            self.thread_obj = self.get_thread_query(thread_id)
            return self.thread_obj
        else:
            raise SuspiciousOperation("No object found")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(thread=self.get_object(), sender=self.get_thread_member())
        ActivityLog.objects.create_log(
            request, actor=self.get_actor_for_activity(), entity=obj, view='MessageView',
            arguments={'args': args, 'kwargs': kwargs}, act_type='send_message'
        )
        # TODO: create notifications, remove members which are mute
        return Response(serializer.data)

    def get_thread_member(self):
        return self.get_actor().threads.get(thread=self.thread_obj)
