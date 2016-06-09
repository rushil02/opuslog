from rest_framework.views import APIView
from rest_framework.response import Response

from messaging_system.models import Thread
from messaging_system.serializers import ThreadSerializer, MessageSerializer


class ThreadView(APIView):
    def get(self, request):
        user = request.user
        threads = Thread.objects.filter(threadmembers__user=user)
        serializer = ThreadSerializer(instance=threads, many=True)
        return Response(serializer.data)


class MessageView(APIView):
    def get(self, request, thread_id):
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response({"status": "Not Found"})

        messages = thread.message_set.order_by('sent_at').all()
        serializer = MessageSerializer(instance=messages, many=True)
        return Response(serializer.data)
