from rest_framework import serializers

from publication.models import Publication


class PublicationSerializer(serializers.ModelSerializer):
    """ Used for getting publication details - __all__ """

    class Meta:
        model = Publication
        fields = '__all__'


class PublicationSerializerTwo(serializers.ModelSerializer):
    """ Used for getting publication details - name, handler, logo """

    url = serializers.CharField(source='get_handler_url', read_only=True)

    class Meta:
        model = Publication
        fields = ('name', 'handler', 'logo', 'url')
