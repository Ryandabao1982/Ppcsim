from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        # Ensure username is set if it's still a required model field,
        # or handle its absence if you've set username=None.
        # If username is kept but made optional, it might not need to be in create_user signature.
        # For now, let's assume AbstractUser still expects username, so we generate one or make it optional.
        # The model below makes username optional, so we don't strictly need it here if not provided.

        # If username is not part of extra_fields, we can derive it or leave it blank
        # if extra_fields.get('username') is None:
        #     extra_fields['username'] = email.split('@')[0] # Example default username

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        # If 'username' is required by your setup for superuser but not for regular user:
        if not extra_fields.get('username') and 'username' in self.model.REQUIRED_FIELDS:
             extra_fields['username'] = email.split('@')[0] # Or some default

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    # Set username to None to remove it completely.
    # This requires more changes (e.g. in admin, forms).
    # username = None

    # Alternative: make username optional and not unique if email is the primary identifier.
    # AbstractUser's username field is unique by default. We need to override it.
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,  # No longer unique
        null=True,     # Can be null in DB
        blank=True,    # Can be blank in forms
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )
    email = models.EmailField(_('email address'), unique=True) # Email is now the unique identifier

    # first_name and last_name are already in AbstractUser.
    # is_active, is_staff, is_superuser, date_joined are also from AbstractUser.

    USERNAME_FIELD = 'email'
    # If username is truly optional/removed, it shouldn't be in REQUIRED_FIELDS.
    # Default REQUIRED_FIELDS for AbstractUser is ['username']. We must override this.
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Add any other fields you want required during createsuperuser

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
