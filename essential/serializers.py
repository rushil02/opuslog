from rest_framework import serializers

from essential.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('write_up', 'notification_type', 'data', 'notified', 'add_on_actor_count')
