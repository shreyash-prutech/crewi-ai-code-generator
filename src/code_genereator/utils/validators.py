import re

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def is_valid_email(email: str) -> bool:
    """Return True if email is syntactically valid, False otherwise.
    
    This is a simple validation intended for lightweight checks (not full RFC 5322 compliance).
    """
    if not isinstance(email, str):
        return False
    email = email.strip()
    if not email:
        return False
    return bool(EMAIL_REGEX.fullmatch(email))

__all__ = ["is_valid_email"]
