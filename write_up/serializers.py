from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from essential.models import Permission
from publication.models import Publication


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('code_name',)


class AddContributorWriteUpSerializer(serializers.Serializer):
    handler = serializers.CharField(max_length=30, source='get_contributor_handler')
    permissions = PermissionSerializer(many=True)
    share_XP = serializers.DecimalField(max_value=100, min_value=0, max_digits=8, decimal_places=5)
    share_money = serializers.DecimalField(max_value=100, min_value=0, max_digits=8, decimal_places=5)

    def validate_handler(self, value):
        handler = value

        try:
            self.obj = get_user_model().objects.get(username=handler)
        except ObjectDoesNotExist:
            try:
                self.obj = Publication.objects.get(handler=handler)
            except ObjectDoesNotExist:
                raise ValidationError("Object does not exist")
        return value

    def validate_permissions(self, value):
        queryset = Permission.objects.filter(permission_type='W')
        for permission in value:
            queryset = queryset.filter(code_name=permission['code_name'])
        if not queryset.exists():
            raise ValidationError("Permission does not exists")
        return value
