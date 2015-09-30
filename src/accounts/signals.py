from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# OAuth Application
from oauth2_providers.models import Application

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_client(sender, instance=None, created=False, **kwargs):
    '''
    Intented to be used as a receiver function for the `post_save` signal
    on a custom User model.

    Creates client_id and client_secret for authenticated users.
    '''
    if created:
        Application.objects.create(user=instance,
                                client_id = Application.CLIENT_CONFIDENTIAL,
                                authorization_grant_type = Application.GRANT_PASSWORD
                                )
