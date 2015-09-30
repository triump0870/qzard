from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialSignUpSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('name', 'password', 'client_id', 'client_secret')
        write_only_fields = ('password',)

    def get_client_id(self, obj):
        return obj.application_set.first().client_id

    def get_client_secret(self, obj):
        return obj.application_set.first().client_secret
