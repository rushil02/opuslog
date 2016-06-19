import re

from django.contrib.auth import get_user_model

from django.db.models.expressions import F

from Opuslog.celery import app
from essential.models import Notification


@app.task(name='post_process_comment')
def process_comment(comment_id):
    # Get object
    comment = getattr(__import__('engagement.models', fromlist=['Comment']), 'Comment').objects.get(id=comment_id)

    # Increase parent comment counter
    if comment.reply_to:
        comment.reply_to.replies_num = F('replies_num') + 1
        comment.reply_to.save()

    # Parse text to find all attached users
    username_list = [x.strip('@') for x in re.findall(r'\B@\w+', comment.comment_text)]
    for username in username_list:
        try:
            user = get_user_model().objects.get(username=username)  # TODO: for publisher
        except get_user_model().DoesNotExist:
            pass
        else:
            if not user == comment.actor:
                Notification.objects.notify(user=user, write_up=comment.write_up, notification_type='CT')
