"""
Validators for user input.
Implements validation requirements from section 3.3 of the specification.
"""

import re
from datetime import datetime, date
from decimal import Decimal


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_inn(inn: str) -> bool:
    """
    Validate Russian INN (tax ID).
    Must be 10 or 12 digits.
    """
    if not inn:
        return True  # INN is optional
    pattern = r'^[0-9]{10,12}$'
    return bool(re.match(pattern, inn))


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return True  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic validation)."""
    if not phone:
        return True  # Phone is optional
    # Allow digits, spaces, dashes, parentheses, plus sign
    pattern = r'^[\d\s\-\(\)\+]+$'
    return bool(re.match(pattern, phone)) and len(re.sub(r'\D', '', phone)) >= 10


def validate_positive_number(value, allow_zero: bool = False) -> bool:
    """Validate that a value is a positive number."""
    try:
        num = Decimal(str(value))
        if allow_zero:
            return num >= 0
        return num > 0
    except:
        return False


def validate_quantity(quantity) -> bool:
    """Validate quantity (must be positive, up to 3 decimal places)."""
    try:
        qty = Decimal(str(quantity))
        if qty <= 0:
            return False
        # Check decimal places
        if qty.as_tuple().exponent < -3:
            return False
        return True
    except:
        return False


def validate_price(price) -> bool:
    """Validate price (must be non-negative, up to 2 decimal places)."""
    try:
        p = Decimal(str(price))
        if p < 0:
            return False
        # Check decimal places
        if p.as_tuple().exponent < -2:
            return False
        return True
    except:
        return False


def validate_date_not_future(dt: date) -> bool:
    """Validate that date is not in the future."""
    return dt <= date.today()


def validate_date_not_past(dt: date) -> bool:
    """Validate that date is not in the past."""
    return dt >= date.today()


def validate_expiry_date(arrival_date: date, expiry_date: date, shelf_life_days: int) -> tuple:
    """
    Validate expiry date against arrival date and shelf life.
    Returns (is_valid, error_message)
    """
    if expiry_date <= arrival_date:
        return False, "Срок годности должен быть больше даты поступления"
    
    actual_shelf_life = (expiry_date - arrival_date).days
    if actual_shelf_life > shelf_life_days:
        return False, f"Срок годности превышает установленный ({shelf_life_days} дн.)"
    
    return True, ""


def validate_login(login: str) -> bool:
    """Validate login format."""
    if not login or len(login) < 3:
        return False
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, login))


def validate_password(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    return True, ""


def validate_string_not_empty(value: str, field_name: str = "Поле") -> tuple:
    """Validate that string is not empty."""
    if not value or not value.strip():
        return False, f"{field_name} не может быть пустым"
    if len(value.strip()) > 150:
        return False, f"{field_name} слишком длинное (макс. 150 символов)"
    return True, ""


def validate_batch_number(batch_number: str) -> bool:
    """Validate batch number format."""
    if not batch_number:
        return True  # Can be auto-generated
    return len(batch_number.strip()) <= 50


VALID_UNITS = ('кг', 'шт', 'уп')


def validate_unit(unit: str) -> bool:
    """Validate unit of measurement."""
    return unit in VALID_UNITS


VALID_ROLES = ('admin', 'manager', 'cashier')


def validate_role(role: str) -> bool:
    """Validate user role."""
    return role in VALID_ROLES


VALID_WRITE_OFF_REASONS = ('expired', 'damaged', 'quality_check', 'other')


def validate_write_off_reason(reason: str) -> bool:
    """Validate write-off reason."""
    return reason in VALID_WRITE_OFF_REASONS
