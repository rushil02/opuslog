from django.core.exceptions import SuspiciousOperation
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView

from rest_framework.response import Response

from custom_package.mixins import AbstractMixin
from essential.models import RequestLog
from messaging_system.models import Message, ThreadMember
from messaging_system.serializers import ThreadSerializer, MessageSerializer, AddMemberSerializer


class Mixin(AbstractMixin):
    def get_thread_query(self, thread_id):
        raise NotImplementedError("Override in subclass")


class ThreadView(Mixin, ListAPIView):
    """
    Return list of threads of a user, creates a new entry and updates a given
    thread's subject.
    """

    serializer_class = ThreadSerializer

    obj = None

    def notify_post(self, obj):
        return

    def post(self, request, *args, **kwargs):
        """ Create new Thread and assign thread creator as thread member """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user)
        obj.threadmember_set.create(entity=self.get_actor())
        self.log(request, obj, args, kwargs, 'create_thread', 'messaging_system.views.ThreadView.post')
        self.notify_post(obj)
        return Response(serializer.data)

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
        self.log(request, obj, args, kwargs, 'update_thread_subject', 'messaging_system.views.ThreadView.patch')
        self.notify_multiple(
            model='messaging_system.ThreadMember', method='get_thread_members_for_thread',
            method_kwargs={'thread_id': obj.id}, entity='entity', notification_type='UT',
            acted_on=obj, old_subject=old_subject,
            template_key='single',
        )
        return Response(serializer.data)


class AddDeleteMemberView(Mixin, GenericAPIView):
    """ Add/Delete a member for a thread. Only owner can add or delete a member. """

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
        serializer = self.get_serializer(data=request.data, thread=self.get_object(), method_type='post')
        serializer.is_valid(raise_exception=True)
        try:
            obj = RequestLog.objects.create(request_for=self.get_object(), request_to=serializer.obj,
                                            request_from=self.get_actor())
        except IntegrityError:
            raise ValidationError("A request has already been sent to the desired user")
        except Exception as e:
            raise ValidationError(e.message)
        else:
            self.notify_single(
                user=serializer.obj,
                user_handler=serializer.obj.get_handler(),
                notification_type='RL',
                file_path='messaging_system.models',
                attr_path='ThreadMember.objects.add_thread_member_request',
                request_log_id=obj.id,
                acted_on=self.get_object(),
                template_key='add_thread_member',
                self_template_key='add_thread_member_internal_publication'
            )
            self.log(request, obj, args, kwargs, 'add_member', 'messaging_system.views.AddDeleteMemberView.post')
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, thread=self.get_object(), method_type='delete')
        serializer.is_valid(raise_exception=True)
        try:
            obj = ThreadMember.objects.get(thread=self.get_object(), entity=serializer.obj).update(removed=True)
        except Exception as e:
            raise ValidationError(e.message)
        else:
            self.log(request, obj, args, kwargs, 'delete_member', 'messaging_system.views.AddDeleteMemberView.delete')
            self.notify_single(
                notify_self_pub=False,
                user=serializer.obj,
                notification_type='DM',
                template_key='directed_to',
                acted_on=self.get_object(),
            )
            self.notify_multiple(
                model='messaging_system.ThreadMember', method='get_thread_members_for_thread',
                method_kwargs={'thread_id': obj.id}, entity='entity', notification_type='UT',
                template_key='single',
                acted_on=self.get_object(),
                acted_on_user=serializer.obj.get_handler(),
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
        self.log(request, obj, args, kwargs, 'send_message', 'messaging_system.views.MessageView.post')
        self.notify_multiple(
            model='messaging_system.ThreadMember', method='get_thread_members_for_thread',
            method_kwargs={'thread_id': self.get_object().id}, entity='entity', notification_type='NM',
            acted_on=self.get_object(),
        )
        return Response(serializer.data)

    def get_thread_member(self):
        return self.get_actor().threads.get(thread=self.thread_obj)
