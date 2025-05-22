"""
Password Utilities

This module provides functions for password hashing and validation.
"""

import re
from werkzeug.security import generate_password_hash, check_password_hash

# Password requirements
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGITS = True
REQUIRE_SPECIAL_CHARS = True
SPECIAL_CHARS = r'[!@#$%^&*(),.?":{}|<>]'

class PasswordError(Exception):
    """Exception raised for password validation errors."""
    pass

def hash_password(password):
    """
    Hash a password using Werkzeug's secure password hashing.
    
    Args:
        password (str): The plaintext password to hash
        
    Returns:
        str: The hashed password
    """
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """
    Check if a password matches its hashed version.
    
    Args:
        hashed_password (str): The hashed password
        password (str): The plaintext password to check
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return check_password_hash(hashed_password, password)

def validate_password_strength(password):
    """
    Validate that a password meets strength requirements.
    
    Args:
        password (str): The password to validate
        
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is a string
    """
    if not password or not isinstance(password, str):
        return False, "Password must be a string"
    
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must be at most {MAX_PASSWORD_LENGTH} characters long"
    
    if REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if REQUIRE_DIGITS and not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if REQUIRE_SPECIAL_CHARS and not re.search(SPECIAL_CHARS, password):
        return False, f"Password must contain at least one special character: {SPECIAL_CHARS}"
    
    # Check for common passwords or patterns
    common_passwords = [
        'password', '123456', 'qwerty', 'letmein', 'welcome',
        '123456789', '12345678', '12345', '1234567', '1234567890',
        'admin', 'password1', '123123', '1234', '12345678910',
        'qwerty123', '1q2w3e4r', 'iloveyou', '000000', 'abc123'
    ]
    
    if password.lower() in common_passwords:
        return False, "Password is too common or easily guessable"
    
    # Check for sequential characters (e.g., '1234', 'abcd')
    if re.search(r'(?:123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
        return False, "Password contains sequential characters"
    
    # Check for repeated characters (e.g., 'aaaa', '1111')
    if re.search(r'(.)\1{2,}', password.lower()):
        return False, "Password contains too many repeated characters"
    
    return True, "Password is strong"

def generate_secure_password(length=16):
    """
    Generate a secure random password that meets all requirements.
    
    Args:
        length (int): Length of the password to generate
        
    Returns:
        str: A secure random password
    """
    import random
    import string
    
    if length < MIN_PASSWORD_LENGTH:
        length = MIN_PASSWORD_LENGTH
    elif length > MAX_PASSWORD_LENGTH:
        length = MAX_PASSWORD_LENGTH
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    # Ensure at least one character from each required set
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # Fill the rest of the password with random characters
    all_chars = lowercase + uppercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(length - len(password)))
    
    # Shuffle to avoid predictable patterns
    random.shuffle(password)
    
    return ''.join(password)
