from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import UserProfile

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Retrieve the user based on the email
            user = UserProfile.objects.get(email=username)
            # Check if the password matches the hashed password stored in the database
            if check_password(password, user.password):
                return user
        except UserProfile.DoesNotExist:
            return None
