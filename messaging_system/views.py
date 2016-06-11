import abc

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from messaging_system.models import Thread, Message, ThreadMembers
from messaging_system.serializers import ThreadSerializer, MessageSerializer, AddMemberSerializer


class ThreadView(ListAPIView):
    """
    Return list of threads of a user, creates a new entry and updates a given
    thread's subject.
    """

    serializer_class = ThreadSerializer

    @abc.abstractmethod
    def get_entity(self):
        raise NotImplementedError("Override in subclass")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user)
        obj.threadmembers_set.create(entity=self.get_entity())
        return Response(serializer.data)

    def get_object(self):
        thread_id = self.kwargs.get('thread_id', None)
        if thread_id:
            return get_object_or_404(Thread, id=thread_id)
        else:
            raise SuspiciousOperation("No object found")

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AddDeleteMemberView(GenericAPIView):
    """ Add/Delete a member for a thread. """

    serializer_class = AddMemberSerializer

    def get_queryset(self):
        return ThreadMembers.objects.all()

    def get_object(self):
        thread_id = self.kwargs.get('thread_id', None)
        if thread_id:
            return get_object_or_404(Thread, id=thread_id)
        else:
            raise SuspiciousOperation("No object found")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ThreadMembers.objects.create(thread=self.get_object(), entity=serializer.obj)
        except Exception as e:
            raise ValidationError(e.message)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ThreadMembers.objects.get(thread=self.get_object(), entity=serializer.obj).update(removed=True)
        except Exception as e:
            raise ValidationError(e.message)
        return Response(serializer.data)


class MessageView(ListAPIView):
    """ Add and List messages. """

    def get_queryset(self):
        return Message.objects.filter(thread=self.kwargs.get('thread_id'))

    serializer_class = MessageSerializer

    def get_thread(self):
        return get_object_or_404(Thread, id=self.kwargs.get('thread_id'))

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(thread=self.get_thread(), sender=request.user)
        return Response(serializer.data)
