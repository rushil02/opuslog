from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Used for getting User details - username, first_name,
    last_name, email, publication_identity and profile_image
    """

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'publication_identity', 'profile_image')


class UserSerializerTwo(serializers.ModelSerializer):
    """
    Used for getting User details - username, first_name,
    and profile_image.
    """

    url = serializers.CharField(source='get_handler_url', read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'profile_image', 'url')
