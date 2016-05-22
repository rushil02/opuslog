from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from essential.models import Notification
from essential.serializers import NotificationSerializer


class NotificationView(APIView):
    query = Notification.objects.get_notification
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        notifications = self.query(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class AllNotificationView(APIView):
    query = Notification.objects.get_all_notification
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        notifications = self.query(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
