from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from essential.models import WriteUpContributor, Permission
from publication.permissions import PublicationContributorPermissionMixin, PublicationContributorGroupPermissionMixin
from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, VoteWriteupView, \
    SubscriberView, VoteCommentView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView
from write_up.views import CreateWriteUpView, EditWriteUpView, EditBaseDesign, CollectionUnitView


class GetActor(object):
    """ For Method inherited by every Publication API class."""

    actor = None

    def get_actor(self):
        return self.publication_contributor.publication

    def get_actor_handler(self):
        return self.get_actor().handler

    def get_success_url_prefix(self):
        return "/pub/" + self.get_actor_handler()

    def get_actor_for_activity(self):
        return self.publication_contributor

    def get_user(self):
        return self.request.user

    def get_redirect_url(self):
        return ""

    def notify_single(self, **kwargs):
        super(GetActor, self).notify_single(contributor=self.get_user().username, **kwargs)

    def notify_multiple(self, **kwargs):
        super(GetActor, self).notify_multiple(contributor=self.get_user().username, **kwargs)


class PublicationThreads(GetActor, PublicationContributorPermissionMixin, ThreadView):
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


class AddDeleteMemberToThread(GetActor, PublicationContributorPermissionMixin, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for Publication entity. """

    publication_permissions = {'post': ['create_ThreadMember'], 'delete': ['delete_ThreadMember']}
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())


class MessageOfThread(GetActor, PublicationContributorPermissionMixin, MessageView):
    """ Implements MessageView for Publication entity. """

    publication_permissions = {'get': ['read_messages'], 'post': ['create_messages'], }
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())

    def set_user(self):
        return self.request.user


def publication_page(request, pub_handler):
    # TODO: redirect to this page when requested for a publication's detail page
    return HttpResponse("You reached on some other publication's {%s} home page" % pub_handler)


class PublicationCommentFirstLevel(GetActor, CommentFirstLevelView):
    """ Implements PublicationView for posting/fetching first level comments. """
    pass


class PublicationCommentNested(GetActor, CommentNestedView):
    """ Implements PublicationView for posting/fetching nested comments. """
    pass


class PublicationCommentDelete(GetActor, DeleteCommentView):
    """ Implements PublicationView for deleting any comment. """
    pass


class PublicationVoteWriteup(GetActor, VoteWriteupView):
    """ Implements PublicationView for up/down voting a writeup, or deleting so """
    pass


class PublicationSubscriber(GetActor, SubscriberView):
    """ Implements PublicationView for Subscribing a publication or user """
    pass


class PublicationVoteComment(GetActor, VoteCommentView):
    """ Implements PublicationView for up/down voting a comment, or deleting so """
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
