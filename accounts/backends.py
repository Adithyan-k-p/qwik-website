from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1. Ensure username and password exist
        if username is None or password is None:
            return None

        try:
            # 2. Try to get the user
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple found, grab the first one
            user = User.objects.filter(email=username).order_by('id').first()

        # 3. FIX: Check 'if user' before calling check_password
        # This prevents "None has no attribute check_password"
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None