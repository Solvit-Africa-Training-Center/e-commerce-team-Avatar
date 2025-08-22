from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import random

# -------------------------------
# Utility for OTP generation
# -------------------------------
def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

# -------------------------------
# User Manager
# -------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, full_name, password, **extra_fields)

# -------------------------------
# User Model
# -------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=[
        ('client', 'Client'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ], default='client')

    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

# -------------------------------
# Seller Profile Model
# -------------------------------
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=255)
    store_logo = models.ImageField(upload_to="store_logos/", blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="deleted_seller_profiles"
    )

    def __str__(self):
        return f"{self.store_name} ({self.user.email})"

# -------------------------------
# Location Model
# -------------------------------
class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="locations")
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"

# -------------------------------
# Email OTP
# -------------------------------
class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @classmethod
    def create_otp(cls, user, ttl_minutes=5):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        otp_code = generate_otp()
        now = timezone.now()
        otp_obj = cls.objects.create(
            user=user,
            otp=otp_code,
            expires_at=now + timedelta(minutes=ttl_minutes)
        )
        return otp_obj

    def is_expired(self):
        return timezone.now() > self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save()
