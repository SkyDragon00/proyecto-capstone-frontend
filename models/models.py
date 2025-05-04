from fastapi import UploadFile
from datetime import date
from pydantic import BaseModel, EmailStr, Field
from pydantic import BaseModel


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
    scope: str


# Model for the signup form
"""
        <form method="post" action="/signup" id="login-form">
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

            <div class="input-group">
                <div>
                    <label for="id_number">Identificación:</label>
                    <input type="text" id="id_number" name="id_number" required placeholder="xxxxxxxxxx">
                </div>
                <div>
                    <label for="id_number_type">Tipo de Identificación:</label>
                    <select id="id_number_type" name="id_number_type" required>
                        <option value="" disabled selected>Selecciona una opción</option>
                        <option value="cedula">Cédula</option>
                        <option value="passport">Pasaporte</option>
                    </select>
                </div>
            </div>

            <div class="input-group">
                <div>
                    <label for="phone">Teléfono:</label>
                    <input type="text" id="phone" name="phone" required placeholder="xxxxxxxxxx">
                </div>
                <div>
                    <label for="gender">Género:</label>
                    <select id="gender" name="gender" required>
                        <option value="" disabled selected>Selecciona una opción</option>
                        <option value="male">Masculino</option>
                        <option value="female">Femenino</option>
                        <option value="other">Otro</option>
                    </select>
                </div>
            </div>

            <label for="date_of_birth">Fecha de Nacimiento:</label>
            <input type="date" id="date_of_birth" name="date_of_birth" required placeholder="dd/mm/yyyy">

            <label for="image">Foto de Perfil:</label>
            <input type="file" id="image" name="image" accept="image/*" required placeholder="Selecciona una imagen">

            <label for="email">Correo:</label>
            <input type="email" id="email" name="email" required placeholder="ejemplo@gmail.com">

            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required placeholder="••••••••">

            <label for="confirm_password">Confirmar Contraseña:</label>
            <input type="password" id="confirm_password" name="confirm_password" required placeholder="••••••••">

            <div class="checkbox-container flex-center">
                <input type="checkbox" id="accepted_terms" name="accepted_terms" required>
                <label for="accepted_terms">
                    <a href="/terms" target="_blank">
                        Acepto los términos y condiciones
                    </a>
                </label>
            </div>

            <button type="submit" class="a-button-filled-red">Registrarse</button>
        </form>
"""


class SignupForm(BaseModel):
    """Class representing the signup form data.

    \f

    :param first_name: First name of the user.
    :type first_name: str

    :param last_name: Last name of the user.
    :type last_name: str

    :param id_number: Identification number of the user.
    :type id_number: str

    :param id_number_type: Type of identification (e.g., cedula, passport).
    :type id_number_type: str

    :param phone: Phone number of the user.
    :type phone: str

    :param gender: Gender of the user.
    :type gender: str

    :param date_of_birth: Date of birth of the user.
    :type date_of_birth: date

    :param image: Profile image of the user.
    :type image: UploadFile

    :param email: Email address of the user.
    :type email: EmailStr

    :param password: Password of the user.
    :type password: str

    :param confirm_password: Confirm password for verification.
    :type confirm_password: str

    :param accepted_terms: Flag indicating acceptance of terms and conditions.
    :type accepted_terms: bool
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    id_number: str = Field(max_length=10)
    id_number_type: str = Field(max_length=20)
    phone: str = Field(max_length=10)
    gender: str = Field(max_length=10)
    date_of_birth: date = Field(description="Date of birth of the user")
    image: UploadFile = Field(description="Profile image of the user")
    email: EmailStr = Field(description="Email address of the user")
    password: str = Field(description="Password of the user")
    confirm_password: str = Field(
        description="Confirm password for verification")
    accepted_terms: bool = Field(
        description="Flag indicating acceptance of terms and conditions")
