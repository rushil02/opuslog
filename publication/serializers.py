from rest_framework import serializers

from publication.models import Publication


class PublicationSerializer(serializers.ModelSerializer):  # TODO: restrict fields
    """ Used for getting publication details - __all__ """

    class Meta:
        model = Publication
        fields = '__all__'


class PublicationMembersSerializer(serializers.ModelSerializer):
    """ Used for getting publication details - name, handler, logo """

    class Meta:
        model = Publication
        fields = ('name', 'handler', 'logo')
