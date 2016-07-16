from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse

from django.shortcuts import get_object_or_404

from custom_package.mixins import PublicationMixin
from engagement.models import Comment
from essential.views import AcceptDenyRequest
from essential.models import WriteUpContributor, Permission
from publication.permissions import PublicationContributorPermissionMixin, PublicationContributorGroupPermissionMixin
from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, VoteWriteupView, \
    SubscriberView, VoteCommentView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView
from write_up.views import CreateWriteUpView, EditWriteUpView, EditBaseDesign, CollectionUnitView


class PublicationThreads(PublicationContributorPermissionMixin, PublicationMixin, ThreadView):
    """ Implements ThreadView for Publication entity. """

    # permissions = ['access_threads']
    publication_permissions = {'get': ['read_threads'], 'post': ['create_threads'], 'patch': ['update_threads']}
    permission_classes = []

    def get_queryset(self):
        try:
            return Thread.objects.filter(threadmember__publication=self.get_actor()).prefetch_related('created_by')
        except Exception as e:
            raise SuspiciousOperation(e.message)

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())

    def notify_post(self, obj):
        self.notify_self(
            notification_type='NT', acted_on=obj,
        )


class AddDeleteMemberToThread(PublicationContributorPermissionMixin, PublicationMixin, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for Publication entity. """

    publication_permissions = {'post': ['create_ThreadMember'], 'delete': ['delete_ThreadMember']}
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, publication=self.get_actor())


class MessageOfThread(PublicationContributorPermissionMixin, PublicationMixin, MessageView):
    """ Implements MessageView for Publication entity. """

    publication_permissions = {'get': ['read_messages'], 'post': ['create_messages'], }
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())


def publication_page(request, pub_handler):
    # TODO: redirect to this page when requested for a publication's detail page
    return HttpResponse("You reached on some other publication's {%s} home page" % pub_handler)


class PublicationCommentFirstLevel(PublicationContributorPermissionMixin, PublicationMixin, CommentFirstLevelView):
    """ Implements PublicationView for posting/fetching first level comments. """
    pass


class PublicationCommentNested(PublicationContributorPermissionMixin, PublicationMixin, CommentNestedView):
    """ Implements PublicationView for posting/fetching nested comments. """
    pass


class PublicationCommentDelete(PublicationContributorPermissionMixin, PublicationMixin, DeleteCommentView):
    """ Implements PublicationView for deleting any comment. """

    def get_comment(self):
        comment_id = self.kwargs.get('comment_id', None)
        if comment_id:
            return get_object_or_404(Comment, id=comment_id, publication=self.get_actor())
        else:
            raise SuspiciousOperation("No object found")


class PublicationVoteWriteup(PublicationContributorPermissionMixin, PublicationMixin, VoteWriteupView):
    """ Implements PublicationView for up/down voting a writeup, or deleting so """
    pass


class PublicationSubscriber(PublicationContributorPermissionMixin, PublicationMixin, SubscriberView):
    """ Implements PublicationView for Subscribing a publication or user """
    pass


class PublicationVoteComment(PublicationContributorPermissionMixin, PublicationMixin, VoteCommentView):
    """ Implements PublicationView for up/down voting a comment, or deleting so """
    pass


class PublicationRequest(PublicationContributorPermissionMixin, PublicationMixin, AcceptDenyRequest):
    """"""
    pass


class PublicationCreateWriteUpView(GetActor, PublicationContributorPermissionMixin, CreateWriteUpView):
    def get_groups(self):
        return self.get_actor().group.get_groups_for_publication_user_to_create(self.get_actor_for_activity())

    def set_object_level_permission_for_publication_user(self):
        WriteUpContributor.objects.create_object_with_permissions(self.object, self.publication_contributor,
                                                                  permission_list=['can_edit'])


publication_create_write_up_view = login_required()(PublicationCreateWriteUpView.as_view())


class PublicationEditWriteUpView(GetActor, PublicationContributorPermissionMixin,
                                 PublicationContributorGroupPermissionMixin, EditWriteUpView):
    write_up_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    group_permissions = {'get': ['can_edit'], 'post': ['can_edit']}

    def user_has_perm(self):
        permission_obj = Permission.objects.get(code_name='can_change_write_up_group')
        if permission_obj in self.publication_contributor.permissions.all():
            return True
        else:
            return False

    def post_group_change(self, new_group):
        WriteUpContributor.objects.delete_contributors_not_in_group(self.object, new_group)


publication_edit_write_up_view = login_required()(PublicationEditWriteUpView.as_view())


class PublicationEditIndependentArticleView(GetActor, PublicationContributorPermissionMixin,
                                            PublicationContributorGroupPermissionMixin, EditBaseDesign):
    write_up_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    group_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    collection_type = 'I'


publication_edit_article_view = login_required()(PublicationEditIndependentArticleView.as_view())


class PublicationCollectionUnitView(GetActor, PublicationContributorPermissionMixin,
                                    PublicationContributorGroupPermissionMixin, CollectionUnitView):
    write_up_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    group_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    collection_type = 'M'


publication_collection_unit_view = login_required()(PublicationCollectionUnitView.as_view())


class EditUserCollectionArticleView(GetActor, PublicationContributorPermissionMixin,
                                    PublicationContributorGroupPermissionMixin, EditBaseDesign):
    write_up_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    group_permissions = {'get': ['can_edit'], 'post': ['can_edit']}
    collection_type = 'M'


publication_edit_collection_article_view = login_required()(EditUserCollectionArticleView.as_view())
