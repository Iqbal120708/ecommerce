import logging

logger = logging.getLogger("auth.audit")

def log_refresh_success(request, user_id):
    logger.info(
        "refresh token success",
        extra={
            "event_type": "token_refresh",
            "status": "success",
            "user_id": user_id,
            "ip_address": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT"),
        }
    )
    
def log_refresh_failure(request, user_id, error_msg):
    logger.warning(
        error_msg,
        extra={
            "event_type": "token_refresh",
            "status": "failure",
            "user_id": user_id,
            "ip_address": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT"),
        }
    )