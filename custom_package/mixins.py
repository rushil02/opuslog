from django.contrib.contenttypes.models import ContentType

from admin_custom.models import ActivityLog
from essential.tasks import notify_async, notify_list_async, notify_self_async


# region Get Actor Mixin
class AbstractGetActorMixin(object):
    def get_user(self):
        return self.request.user

    def get_actor(self):
        raise NotImplementedError("Override in subclass")

    def get_actor_for_activity(self):
        raise NotImplementedError("Override in subclass")

    def get_actor_handler(self):
        return self.get_actor().get_handler()

    def get_permissions(self):
        return []

    def get_redirect_url(self):
        return None


class UserGetActorMixin(AbstractGetActorMixin):
    def get_actor(self):
        return self.get_user()

    def get_actor_for_activity(self):
        return self.get_user()


class PublicationGetActorMixin(AbstractGetActorMixin):
    """
    Will not work without PublicationContributorPermissionMixin as it
    sets the 'contributor' in View class.
    """

    def get_actor(self):
        return self.contributor.publication

    def get_actor_for_activity(self):
        return self.get_actor().contributorlist_set.get(contributor=self.get_user())


# endregion


# region Activity Log Mixin
class AbstractCreateLogMixin(object):
    def log(self, request, obj, m_args, m_kwargs, act_type, view, **kwargs):
        raise NotImplementedError("Override in subclass")

    def log_no_user(self, request, obj, m_args, m_kwargs, act_type, view, **kwargs):
        raise NotImplementedError("Override in subclass")


class CreateLogMixin(object):
    """ log method will not work without GetActor Mixin """
    def log(self, request, obj, m_args, m_kwargs, act_type, view, **kwargs):
        ActivityLog.objects.create_log(
            request, actor=self.get_actor_for_activity(), entity=obj, view=view,
            arguments={'args': m_args, 'kwargs': m_kwargs}, act_type=act_type, **kwargs
        )

    def log_no_user(self, request, obj, m_args, m_kwargs, act_type, view, **kwargs):
        ActivityLog.objects.create_log(
            request, actor=None, entity=obj, view=view,
            arguments={'args': m_args, 'kwargs': m_kwargs}, act_type=act_type, **kwargs
        )


# endregion


# region Notification Mixin
class AbstractNotificationMixin(object):
    def notify_single(self, **kwargs):
        raise NotImplementedError("Override in subclass")

    def notify_multiple(self, **kwargs):
        raise NotImplementedError("Override in subclass")


class NotificationMixin(object):
    def notify_single(self, **kwargs):
        user = kwargs.pop('user')
        kwargs.update({'user_object_id': user.id, 'user_content_type': ContentType.objects.get_for_model(user).id})
        acted_on = kwargs.pop('acted_on', None)
        if acted_on:
            kwargs.update({'acted_on_id': acted_on.id,
                           'acted_on_content_type_id': ContentType.objects.get_for_model(acted_on).id})
        notify_async.delay(
            redirect_url=self.get_redirect_url(),
            actor_handler=self.get_actor_handler(),
            permissions=self.get_permissions(),
            **kwargs
        )

    def notify_multiple(self, **kwargs):
        acted_on = kwargs.pop('acted_on', None)
        if acted_on:
            kwargs.update({'acted_on_id': acted_on.id,
                           'acted_on_content_type_id': ContentType.objects.get_for_model(acted_on).id})
        notify_list_async.delay(
            actor_handler=self.get_actor_handler(),
            redirect_url=self.get_redirect_url(),
            permissions=self.get_permissions(),
            **kwargs
        )


class UserNotificationMixin(NotificationMixin):
    pass


class PublicationNotificationMixin(NotificationMixin):
    def notify_single(self, notify_self_pub=True, **kwargs):
        super(PublicationNotificationMixin, self).notify_single(contributor=self.get_user().username, **kwargs)
        if notify_self_pub:
            self.notify_self(**kwargs)

    def notify_multiple(self, notify_self_pub=True, **kwargs):
        super(PublicationNotificationMixin, self).notify_multiple(contributor=self.get_user().username, **kwargs)
        if notify_self_pub:
            self.notify_self(**kwargs)

    def notify_self(self, **kwargs):
        acted_on = kwargs.pop('acted_on', None)
        if acted_on:
            kwargs.update({'acted_on_id': acted_on.id,
                           'acted_on_content_type_id': ContentType.objects.get_for_model(acted_on).id})
        notify_self_async.delay(
            publication_id=self.get_actor().id,
            actor_handler=self.get_actor().handler,
            contributor=self.get_user().username,
            redirect_url=self.get_redirect_url(),
            permissions=self.get_permissions(),
            **kwargs
        )


# endregion


# region Set Mixin
class AbstractMixin(AbstractGetActorMixin, AbstractCreateLogMixin, AbstractNotificationMixin):
    pass


class UserMixin(UserGetActorMixin, CreateLogMixin, UserNotificationMixin):
    pass


class PublicationMixin(PublicationGetActorMixin, CreateLogMixin, PublicationNotificationMixin):
    pass

# endregion
