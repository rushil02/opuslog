from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from essential.models import Notification, RequestLog
from essential.serializers import NotificationSerializer, RequestLogSerializer


class Mixin(object):
    def get_actor(self):
        raise NotImplementedError("Override in subclass")

    def get_thread_query(self, thread_id):
        raise NotImplementedError("Override in subclass")

    def get_actor_for_activity(self):
        raise NotImplementedError("Override in subclass")

    def get_actor_handler(self):
        return NotImplementedError("Override in Subclass")


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


class AcceptDenyRequest(Mixin, GenericAPIView):
    """Request accept and deny [Generic]"""

    serializer_class = RequestLogSerializer

    def post(self, request, *args, **kwargs):
        notification_obj = get_object_or_404(Notification,
                                             id=self.kwargs.get('notification_id', None),
                                             user=self.request.user,
                                             notification_type='RL')
        req_obj = get_object_or_404(RequestLog, id=notification_obj.data['request_log_id'], status='P')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print notification_obj, req_obj, serializer.data
        try:
            file_path = notification_obj.data['file_path']
            attr_list = notification_obj.data['attr_path'].split('.')
            cur_attr = getattr(__import__(file_path, fromlist=[attr_list[0], ]), attr_list[0])
            del attr_list[0]
            for attr in attr_list:
                cur_attr = getattr(cur_attr, attr)
            method_kwargs = notification_obj.data.get('method_kwargs', {})
        except Exception as e:
            pass  # TODO: Activity log
        else:
            redirect_url = cur_attr(answer=serializer.validated_data['answer'],
                                    notification=notification_obj,
                                    request_log=req_obj,
                                    **method_kwargs)

            req_obj.status = serializer.validated_data['answer']
            req_obj.save()
            return Response({'redirect_url': redirect_url})
