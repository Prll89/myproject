# accounts/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Autenticación usando nombre de usuario o correo electrónico.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Intentar obtener el usuario por nombre de usuario
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # Intentar obtener el usuario por correo electrónico
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
