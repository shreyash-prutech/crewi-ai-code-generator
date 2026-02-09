import re

EMAIL_SIMPLE_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def validate_email(email: str) -> bool:
    """
    Validate an email address using a simple, readable regular expression.

    This validator checks for the basic "local@domain.tld" structure, disallows
    whitespace and multiple '@' symbols, and requires a top-level domain of at
    least two letters. It also applies simple maximum length guards for the full
    address and for local/domain parts.

    Notes:
    - This is a pragmatic, minimal validator and does not fully implement RFC 5322.
    - Use this for basic input validation; for strict compliance, use a dedicated library.

    Example:
        is_valid = validate_email("user@example.com")  # True
        is_valid = validate_email("invalid@@example.com")  # False

    Args:
        email: The email address to validate.

    Returns:
        True if the email passes basic validation; otherwise False.
    """
    if not isinstance(email, str):
        return False
    candidate = email.strip()
    if not candidate:
        return False
    if len(candidate) > 254:
        return False
    if not EMAIL_SIMPLE_REGEX.match(candidate):
        return False
    local, domain = candidate.rsplit("@", 1)
    if len(local) > 64 or len(domain) > 253:
        return False
    return True
