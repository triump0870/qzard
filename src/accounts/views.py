from __future__ import unicode_literals

# Django imports
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib import messages
from django.conf import settings

# Rest Framework imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

# Python social auth imports
from social.apps.django_app.utils import load_backend, load_strategy
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.exceptions import AuthAlreadyAssociated

# Other third party app imports
from authtools import views as authviews
from braces import views as bracesviews

# Local imports
from . import forms
from serializer import SocialSignUpSerializer

User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin,
                authviews.LoginView):
    template_name = "accounts/login.html"
    form_class = forms.LoginForm
    form_valid_message = "You're logged in!"
    def form_valid(self, form):
        redirect = super(LoginView, self).form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            ONE_MONTH = 30*24*60*60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", ONE_MONTH)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    url = reverse_lazy('home')


class SignUpView(bracesviews.AnonymousRequiredMixin,
                 bracesviews.FormValidMessageMixin,
                 generic.CreateView):
    form_class = forms.SignupForm
    model = User
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
    form_valid_message = "You're signed up!"

    def form_valid(self, form):
        r = super(SignUpView, self).form_valid(form)
        username = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        user = auth.authenticate(email=username, password=password)
        auth.login(self.request, user)
        return r

class SocialSignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SocialSignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate,)

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request.
        request is necessary for `load_strategy`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = request.data['provider']

        # If this request was made with an authenticated user, try to associate this social
        # account with it
        authed_user = request.user if not request.user.is_anonymous() else None

        # `strategy` is a python-social-auth concept referencing the Python framework to be used (Django, Flask, etc.). By passing `request` to `load_strategy`, PSA knows to use the Django strategy
        strategy = load_strategy(request)
        # Now we get the backend that corresponds to our user's social auth provider
        # e.g., Facebook, Twitter, etc.
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)

        if isinstance(backend, BaseOAuth1):
            # Twitter, for example, uses OAuth1 and requires that you also pass
            # an `oauth_token_secret` with your authentication request
            token = {
                'oauth_token': request.data['access_token'],
                'oauth_token_secret': request.data['access_token_secret'],
            }
        elif isinstance(backend, BaseOAuth2):
            # We're using oauth's implicit grant type (usually used for web and mobile applications), so all we have to pass here is an access_token
            token = request.data['access_token']

        try:
            # if `authed_user` is None, python-social-auth will make a new user,
            # else this social account will be associated with the user you pass in
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            # You can't associate a social account with more than one user
            return Response({"errors": "That social media account is already in use"},
                            status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_active:
            # if the access token was set to an empty string, then save the access token from the request
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                # Facebook for example will return the access_token in its response to you.
                # This access_token is then saved for your future use. However, others
                # e.g., Instagram do not respond with the access_token that you just provided. We save it here so it can be used to make subsequent calls.
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            # Set instance since we are not calling `serializer.save()`
            serializer.instance = user
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            return Response({"errors": "Error with social authentication"},
                            status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(authviews.PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please relogin")
        return super(PasswordChangeView, self).form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'accounts/password-reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/emails/password-reset-email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/password-reset-done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = 'accounts/password-reset-confirm.html'
    form_class = forms.SetPasswordForm
