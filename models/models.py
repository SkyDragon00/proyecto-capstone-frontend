from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
import re
import re


class LoginForm(BaseModel):
    """Class representing the login form data.

    \f

    :param username: Username of the user.
    :type username: str

    :param password: Password of the user.
    :type password: str

    :param grant_type: Grant type for the OAuth2 token request.
    :type grant_type: str

    :param scope: Scope for the OAuth2 token request.
    :type scope: str
    """
    username: str
    password: str
    grant_type: str
    scope: str | None = None


# Model for the signup form
"""
<div class="login-container">
    <div class="login-form">
        <div class="login-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 26 26" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="icon icon-tabler icons-tabler-outline icon-tabler-user-plus">
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
                <path d="M16 19h6" />
                <path d="M19 16v6" />
                <path d="M6 21v-2a4 4 0 0 1 4 -4h4" />
            </svg>

            <h1>Registro</h1>

            <p>Regístrate para acceder a tu cuenta.</p>

        </div>

        <form method="post" action="/signup" id="login-form" enctype="multipart/form-data">
            <div class="input-group">
                <div>
                    <label for="first_name">Nombre:</label>
                    <input type="text" id="first_name" name="first_name" required placeholder="Nombre">
                </div>
                <div>
                    <label for="last_name">Apellido:</label>
                    <input type="text" id="last_name" name="last_name" required placeholder="Apellido">
                </div>
            </div>

            <label for="email">Correo:</label>
            <input type="email" id="email" name="email" required placeholder="ejemplo@gmail.com">

            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required placeholder="••••••••">

            <label for="confirm_password">Confirmar Contraseña:</label>
            <input type="password" id="confirm_password" name="confirm_password" required placeholder="••••••••">

            <button type="submit" class="a-button-filled-red">Registrarse</button>
        </form>
    </div>
</div>
"""


class Staff(BaseModel):
    """Class representing a staff member.

    \f

    :param first_name: First name of the staff member.
    :type first_name: str

    :param last_name: Last name of the staff member.
    :type last_name: str

    :param email: Email address of the staff member.
    :type email: EmailStr

    :param password: Password of the staff member.
    :type password: str

    :param confirm_password: Confirm password for verification.
    :type confirm_password: str
    """
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

class Organizer(BaseModel):
    """Class representing a organizer member.

    \f

    :param first_name: First name of the staff member.
    :type first_name: str

    :param last_name: Last name of the staff member.
    :type last_name: str

    :param email: Email address of the staff member.
    :type email: EmailStr

    :param password: Password of the staff member.
    :type password: str

    :param confirm_password: Confirm password for verification.
    :type confirm_password: str
    """
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

class UserUpdate(BaseModel):
    """Class representing user data for partial updates.

    \f

    :param first_name: First name of the user (optional).
    :type first_name: Optional[str]

    :param last_name: Last name of the user (optional).
    :type last_name: Optional[str]

    :param email: Email address of the user (optional).
    :type email: Optional[EmailStr]

    :param password: New password of the user (optional).
    :type password: Optional[str]
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class AssistantUpdate(BaseModel):
    """Class representing assistant data for partial updates.

    \f

    :param phone: Phone number of the assistant (optional).
    :type phone: Optional[str]

    :param id_number: ID number of the assistant (optional) - accepts both Ecuadorian ID and passport.
    :type id_number: Optional[str]

    :param gender: Gender of the assistant (optional).
    :type gender: Optional[str]

    :param date_of_birth: Date of birth of the assistant (optional).
    :type date_of_birth: Optional[date]
    """
    phone: Optional[str] = None
    id_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None

    @validator('date_of_birth', pre=True)
    def parse_date_of_birth(cls, v):
        print("=== AssistantUpdate date_of_birth validator ===")
        print(f"Input value: {v}")
        print(f"Input type: {type(v)}")
        
        if v is None or v == "":
            print("Date is None or empty, returning None")
            return None
        
        if isinstance(v, date):
            print(f"Already a date object: {v}")
            return v
        
        if isinstance(v, str):
            print(f"String date received: {v}")
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(v, '%Y-%m-%d').date()
                print(f"Parsed date: {parsed_date}")
                return parsed_date
            except ValueError as e:
                print(f"Failed to parse date: {e}")
                raise ValueError(f"Invalid date format. Expected YYYY-MM-DD, got: {v}")
        
        print(f"Unexpected type for date_of_birth: {type(v)}")
        raise ValueError(f"Invalid date type: {type(v)}")

    @validator('id_number')
    def validate_id_number(cls, v):
        print("=== AssistantUpdate id_number validator ===")
        print(f"Input value: {v}")
        
        if v is None or v == "":
            print("ID number is None or empty, returning None")
            return None
        
        # Cédula ecuatoriana: exactamente 10 dígitos
        cedula_pattern = r'^\d{10}$'
        # Pasaporte alfanumérico: 1-3 letras seguidas de 4-8 dígitos
        passport_alphanum_pattern = r'^[A-Za-z]{1,3}\d{4,8}$'
        # Pasaporte numérico: 6-9 dígitos
        passport_numeric_pattern = r'^\d{6,9}$'
        
        import re
        if (re.match(cedula_pattern, v) or 
            re.match(passport_alphanum_pattern, v) or 
            re.match(passport_numeric_pattern, v)):
            print(f"ID number {v} is valid")
            return v
        
        print(f"ID number {v} is invalid")
        raise ValueError("ID number must be either a 10-digit Ecuadorian cédula or a valid passport number")

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }

    @validator('date_of_birth', pre=True)
    def parse_date_of_birth(cls, v):
        """Parse date of birth from string to date object."""
        if v is None or v == "":
            return None
        
        if isinstance(v, str):
            try:
                # Parse ISO format date string
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        
        return v

    @validator('id_number')
    def validate_id_number(cls, v):
        """Validate ID number format - accepts both Ecuadorian ID and passport."""
        if v is None or v.strip() == "":
            return v
        
        # Remove any whitespace
        v = v.strip()
        
        # Ecuadorian ID format: 10 digits
        ecuadorian_id_pattern = r'^\d{10}$'
        
        # Passport format: Letter(s) followed by numbers (more flexible for international passports)
        # Common formats: A1234567, AB123456, ABC12345, etc. (1-3 letters, 4-8 digits)
        passport_pattern = r'^[A-Z]{1,3}\d{4,8}$'
        
        # Alternative passport format: numbers only, 6-9 digits
        passport_numeric_pattern = r'^\d{6,9}$'
        
        if re.match(ecuadorian_id_pattern, v):
            # Additional validation for Ecuadorian ID if needed
            return v
        elif re.match(passport_pattern, v.upper()):
            return v.upper()  # Return in uppercase for consistency
        elif re.match(passport_numeric_pattern, v):
            return v
        else:
            raise ValueError(
                'ID number must be either a valid Ecuadorian ID (10 digits) '
                'or a valid passport (1-3 letters followed by 4-8 digits, or 6-9 digits)'
            )
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None or v.strip() == "":
            return v
        
        # Remove any whitespace and common separators
        v = re.sub(r'[\s\-\(\)]', '', v.strip())
        
        # Ecuadorian phone format: 10 digits starting with 0
        if re.match(r'^0\d{9}$', v):
            return v
        
        # International format without country code: 9 digits
        if re.match(r'^\d{9}$', v):
            return '0' + v  # Add leading zero for Ecuador
        
        # International format with country code +593
        if re.match(r'^(\+593|593)\d{9}$', v):
            return v
        
        raise ValueError(
            'Phone number must be a valid Ecuadorian phone number '
            '(10 digits starting with 0, or international format with +593)'
        )
    
    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender value."""
        if v is None or v.strip() == "":
            return v
        
        valid_genders = ['male', 'female', 'other', 'masculino', 'femenino', 'otro']
        if v.lower() not in valid_genders:
            raise ValueError('Gender must be one of: male, female, other')
        
        # Normalize to English
        gender_map = {
            'masculino': 'male',
            'femenino': 'female', 
            'otro': 'other'
        }
        return gender_map.get(v.lower(), v.lower())


class ProfileUpdateRequest(BaseModel):
    """Class representing a complete profile update request.

    \f

    :param user: User data to update (optional).
    :type user: Optional[UserUpdate]

    :param assistant: Assistant data to update (optional).
    :type assistant: Optional[AssistantUpdate]
    """
    user: Optional[UserUpdate] = None
    assistant: Optional[AssistantUpdate] = None
