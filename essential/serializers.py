from rest_framework import serializers

from essential.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('context', 'notified', 'verbose', 'update_time')
