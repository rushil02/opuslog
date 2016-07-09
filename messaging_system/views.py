import abc

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import SuspiciousOperation
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from admin_custom.models import ActivityLog
from essential.models import RequestLog
from essential.tasks import notify_list_async, notify_async
from messaging_system.models import Message, ThreadMember
from messaging_system.serializers import ThreadSerializer, MessageSerializer, AddMemberSerializer


class Mixin(object):
    def get_actor(self):
        raise NotImplementedError("Override in subclass")

    def get_thread_query(self, thread_id):
        raise NotImplementedError("Override in subclass")

    def get_actor_for_activity(self):
        raise NotImplementedError("Override in subclass")

    def get_actor_handler(self):
        return NotImplementedError("Override in Subclass")

    @abc.abstractmethod
    def get_permissions(self):
        return []

    @abc.abstractmethod
    def get_redirect_url(self):
        return None

    def notify_single(self, **kwargs):
        notify_async.delay(
            redirect_url=self.get_redirect_url(),
            actor_handler=self.get_actor_handler(),
            permissions=self.get_permissions(),
            **kwargs
        )

    def notify_multiple(self, **kwargs):
        notify_list_async.delay(
            actor_handler=self.get_actor_handler(),
            redirect_url=self.get_redirect_url(),
            permissions=self.get_permissions(),
            **kwargs
        )


class ThreadView(Mixin, ListAPIView):  # TODO: create maintenance task to remove Threads with no user/publication
    """
    Return list of threads of a user, creates a new entry and updates a given
    thread's subject.
    """

    serializer_class = ThreadSerializer

    obj = None

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
        return Response(serializer.data), obj.subject

    def get_object(self):
        if self.obj:
            return self.obj
        thread_id = self.kwargs.get('thread_id', None)
        if thread_id:
            obj = self.get_thread_query(thread_id)
            return obj
        else:
            raise SuspiciousOperation("No object found")

    def patch(self, request, *args, **kwargs):
        old_subject = self.get_object().subject
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        ActivityLog.objects.create_log(
            request, actor=self.get_actor_for_activity(), entity=obj, view='ThreadView',
            arguments={'args': args, 'kwargs': kwargs}, act_type='update_thread_subject'
        )
        notify_list_async.delay(
            model='messaging_system.ThreadMember', method='get_thread_members_for_thread',
            method_kwargs={'thread_id': obj.id}, entity='entity', notification_type='UT',
            new_subject=obj.subject, old_subject=old_subject,
            template_key='single',
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
        serializer = self.get_serializer(data=request.data, thread=self.get_object())
        serializer.is_valid(raise_exception=True)
        try:
            obj = RequestLog.objects.create(request_for=self.get_object(), request_to=serializer.obj,
                                            request_from=self.get_actor())
        except Exception as e:
            raise ValidationError(e.message)
        else:
            self.notify_single(
                user_object_id=serializer.obj.id,
                user_content_type=ContentType.objects.get_for_model(serializer.obj).id,
                notification_type='RL',
                file_path='messaging_system.models',
                attr_path='ThreadMember.objects.add_thread_member_request',
                request_log_id=obj.id,
                verbose='You have got a new request'
            )
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

    def get_redirect_url(self):
        return '/request/'


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
