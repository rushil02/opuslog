import re

from django.contrib.auth import get_user_model
from django.db.models.expressions import F

from Opuslog.celery import app
from essential.models import Notification


@app.task(name='post_process_comment')
def process_comment(comment_id, actor_handler):
    # Get object
    comment = getattr(__import__('engagement.models', fromlist=['Comment']), 'Comment').objects.get(id=comment_id)

    # Increase parent comment counter
    if comment.reply_to:
        comment.reply_to.replies_num = F('replies_num') + 1
        comment.reply_to.save()

    # Parse text to find all attached users
    handler_list = [x.strip('@') for x in re.findall(r'\B@\w+', comment.comment_text)]
    for handler in handler_list:
        user = None
        try:
            user = get_user_model().objects.get(username=handler)
        except get_user_model().DoesNotExist:
            try:
                user = getattr(__import__('publication.models', fromlist=['Publication']),
                               'Publication').objects.get(handler=handler)
            except Exception:
                return
        finally:
            if user:
                if not user == comment.actor:
                    Notification.objects.notify(
                        user=user, acted_on=comment.write_up, notification_type='CT', actor_handler=actor_handler,
                        template_key='single'
                    )
