from pydantic import BaseModel, EmailStr
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
