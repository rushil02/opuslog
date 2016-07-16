from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from custom_package.mixins import UserMixin
from engagement.models import Comment
from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, VoteWriteupView, \
    SubscriberView, VoteCommentView
from essential.views import AcceptDenyRequest
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView
from user_custom.serializers import UserTimezoneSerializer


class UserThreads(UserMixin, ThreadView):
    """ Implements ThreadView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(threadmember__user=self.get_actor()).prefetch_related('created_by')

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class AddDeleteMemberToThread(UserMixin, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, user=self.get_actor())


class MessageOfThread(UserMixin, MessageView):
    """ Implements MessageView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class UserCommentFirstLevel(UserMixin, CommentFirstLevelView):
    """ Implements UserView for posting/fetching first level comments. """
    pass


class UserCommentNested(UserMixin, CommentNestedView):
    """ Implements UserView for posting/fetching nested comments. """
    pass


class UserCommentDelete(UserMixin, DeleteCommentView):
    """ Implements UserView for deleting any comment. """

    def get_comment(self):
        comment_id = self.kwargs.get('comment_id', None)
        if comment_id:
            return get_object_or_404(Comment, id=comment_id, user=self.get_actor())
        else:
            raise SuspiciousOperation("No object found")


class UserVoteWriteup(UserMixin, VoteWriteupView):
    """ Implements UserView for up/down voting a writeup, or deleting so"""
    pass


class UserSubscriber(UserMixin, SubscriberView):
    """ Implements UserView for Subscribing a publication or user """
    pass


class UserVoteComment(UserMixin, VoteCommentView):
    """ Implements UserView for up/down voting a comment, or deleting so """
    pass


class UserRequest(UserMixin, AcceptDenyRequest):
    """"""
    pass


@api_view(['POST'])
@permission_classes((AllowAny,))
def set_timezone(request):
    serializer = UserTimezoneSerializer(data=request.data)
    if serializer.is_valid():
        if request.user.is_authenticated():
            user_profile = request.user.userprofile
            user_profile.timezone = serializer.validated_data['tz']
            user_profile.save()
        request.session['django_timezone'] = serializer.validated_data['tz']
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
