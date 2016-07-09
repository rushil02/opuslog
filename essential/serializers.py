from rest_framework import serializers

from essential.models import Notification, RequestLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('context', 'notified', 'verbose', 'update_time')


class RequestLogSerializer(serializers.Serializer):
    answer = serializers.ChoiceField(choices=RequestLog.STATUS)
