from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
import logging

logger = logging.getLogger("auth.audit")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(
        "Login success",
        extra={
            "event_type": "login",
            "user_id": user.id,
            "email": user.email,
            "ip_address": request.META.get("REMOTE_ADDR", "unknown"),
            "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
        }
    )