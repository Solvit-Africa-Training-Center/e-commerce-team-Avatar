import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP, User

def generate_otp(length=6):
    """
    Generate a numeric OTP of specified length.
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def send_otp_email(user: User, ttl_minutes=5):
    """
    Create an OTP for a user and send it via email.
    Returns the OTP object.
    """
    # Invalidate any previous unused OTPs
    EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Create new OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
    otp_obj = EmailOTP.objects.create(
        user=user,
        otp=otp_code,
        expires_at=expires_at
    )
    
    # Send OTP email
    send_mail(
        subject="Your OTP Code",
        message=(
            f"Hello {user.full_name},\n\n"
            f"Your OTP code is: {otp_code}\n"
            f"It will expire in {ttl_minutes} minutes.\n\n"
            "If you did not request this, please ignore this email."
        ),
        from_email="no-reply@yourapp.com",  # better: use environment variable
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return otp_obj


def verify_otp(user: User, otp_code: str) -> bool:
    """
    Verify the OTP for a given user.
    Returns True if valid, False if invalid or expired.
    """
    try:
        otp_obj = EmailOTP.objects.filter(
            user=user, otp=otp_code, is_used=False
        ).latest("created_at")  # pick latest OTP if duplicates exist
        
        if otp_obj.expires_at < timezone.now():
            return False  # expired
        
        otp_obj.mark_as_used()
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        return True
    
    except EmailOTP.DoesNotExist:
        return False
