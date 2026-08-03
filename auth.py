"""
auth.py
───────
Authentication & Validation Layer — F1 Race Analytics Explorer
BCA306-5 Advanced Python | Lab Exercise P6

Provides login/registration with regex-based validation and a
simple in-memory user store (session-scoped — resets when the app
restarts, which is expected for a Streamlit Cloud demo app).
"""

import re
import hashlib


# ─────────────────────────────────────────────────────────────
# PRE-COMPILED PATTERNS
# ─────────────────────────────────────────────────────────────
PATTERNS = {
    "username": re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$'),
    "email":    re.compile(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'),
    "upper":    re.compile(r'[A-Z]'),
    "digit":    re.compile(r'\d'),
    "special":  re.compile(r'[!@#$%^&*(),.?":{}|<>]'),
    "spaces":   re.compile(r'\s{2,}'),
}


def sanitize(value: str) -> str:
    """Collapse repeated whitespace and strip ends."""
    return PATTERNS["spaces"].sub(" ", value or "").strip()


# ─────────────────────────────────────────────────────────────
# FIELD VALIDATORS
# ─────────────────────────────────────────────────────────────
def validate_username(username: str):
    username = sanitize(username)
    if not username:
        return False, "Username cannot be empty."
    if not re.match(r'^[a-zA-Z]', username):
        return False, "Username must start with a letter."
    if not PATTERNS["username"].fullmatch(username):
        return False, "3–20 characters: letters, digits, underscores only."
    return True, "✓ Valid username."


def validate_email(email: str):
    email = sanitize(email)
    if not email:
        return False, "Email cannot be empty."
    if not PATTERNS["email"].fullmatch(email):
        return False, "Invalid email format (name@domain.com)."
    return True, "✓ Valid email."


def validate_password(password: str):
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Minimum 8 characters."
    if not PATTERNS["digit"].search(password):
        return False, "Must contain at least one digit."
    if not PATTERNS["upper"].search(password):
        return False, "Must contain at least one uppercase letter."
    if not PATTERNS["special"].search(password):
        return False, "Must contain at least one special character."
    return True, "✓ Strong password."


def validate_full_name(name: str):
    name = sanitize(name)
    if not name:
        return False, "Full name cannot be empty."
    parts = re.split(r'\s+', name)
    if len(parts) < 2:
        return False, "Enter first and last name."
    if not re.fullmatch(r"^[a-zA-Z\s'-]{3,50}$", name):
        return False, "Letters, spaces, hyphens, apostrophes only."
    return True, "✓ Valid name."


# ─────────────────────────────────────────────────────────────
# FORM-LEVEL VALIDATION
# ─────────────────────────────────────────────────────────────
def validate_registration(username, full_name, email, password, confirm_password):
    errors = {}
    try:
        ok, msg = validate_username(username)
        if not ok: errors["username"] = msg

        ok, msg = validate_full_name(full_name)
        if not ok: errors["full_name"] = msg

        ok, msg = validate_email(email)
        if not ok: errors["email"] = msg

        ok, msg = validate_password(password)
        if not ok: errors["password"] = msg

        if password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."
    except Exception as e:
        errors["__general__"] = f"Unexpected error: {e}"

    return {"valid": len(errors) == 0, "errors": errors}


def validate_login(credential, password):
    errors = {}
    try:
        credential = sanitize(credential)
        if not credential:
            errors["credential"] = "Username or email required."
        if not password:
            errors["password"] = "Password required."
        elif len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
    except Exception as e:
        errors["__general__"] = f"Unexpected error: {e}"

    return {"valid": len(errors) == 0, "errors": errors}


# ─────────────────────────────────────────────────────────────
# USER STORE  (in-memory — resets when the app restarts)
# ─────────────────────────────────────────────────────────────
_USER_DB = {}


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, full_name, email, password):
    username = sanitize(username).lower()
    if username in _USER_DB:
        return False, f"Username '{username}' is already taken."
    if any(u["email"] == email.lower() for u in _USER_DB.values()):
        return False, f"Email '{email}' is already registered."
    _USER_DB[username] = {
        "full_name": sanitize(full_name),
        "email": email.lower(),
        "password_hash": _hash(password),
    }
    return True, f"Account created! Welcome, {full_name.split()[0]}."


def login_user(credential, password):
    credential = sanitize(credential).lower()
    ph = _hash(password)

    if credential in _USER_DB:
        user = _USER_DB[credential]
        if user["password_hash"] == ph:
            return True, f"Welcome back, {user['full_name'].split()[0]}!", user
        return False, "Incorrect password.", {}

    for user in _USER_DB.values():
        if user["email"] == credential:
            if user["password_hash"] == ph:
                return True, f"Welcome back, {user['full_name'].split()[0]}!", user
            return False, "Incorrect password.", {}

    return False, "No account found with that username or email.", {}


def seed_demo_user():
    """Ensures a demo account always exists for quick testing."""
    try:
        register_user("demo", "Demo User", "demo@f1analytics.com", "Demo@1234")
    except Exception:
        pass
