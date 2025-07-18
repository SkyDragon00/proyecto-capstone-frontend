import tempfile
import json
from typing import Annotated
from uuid import UUID
from fastapi import Cookie, FastAPI, Form, HTTPException, Path, Request, UploadFile, File, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import requests

from config import SettingsDependency
from models.models import LoginForm, Staff, UserUpdate, AssistantUpdate, ProfileUpdateRequest
from datetime import datetime
import traceback

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")
templates.env.filters["strftime"] = lambda date_str: (  # type: ignore
    datetime.fromisoformat(date_str.replace(
        'Z', '+00:00')).strftime('%d/%m/%Y %H:%M')
)


@app.get(
    "/home",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the home page"
)
async def home(
    request: Request,
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None
):
    """Endpoint to retrieve the home page with upcoming events.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.API_URL}/events/upcoming?quantity=3")

    events = response.json()

    if not events:
        events = []  # or handle the empty case as needed

    return templates.TemplateResponse(
        request=request,
        name="index.html.j2",
        context={
            "request": request,
            "events": events,
            "role": role
        }
    )


@app.get(
    "/terms",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the terms and conditions page"
)
async def terms(
    request: Request,
):
    """Endpoint to retrieve the terms and conditions page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="terms.html.j2",
    )


@app.get(
    "/event/image/{image_uuid}",
    response_class=FileResponse,
    summary="Endpoint to retrieve the event image",
    response_description="Successful Response with the event image",
)
async def get_event_image(
    image_uuid: Annotated[
        UUID,
        Path(
            title="Image UUID",
            description="The UUID of the event image to retrieve",
        )
    ],
    settings: SettingsDependency
):
    """Endpoint to retrieve the event image.

    \f

    :param image_uuid: UUID of the event image to retrieve.
    :type image_uuid: UUID
    :param settings: SettingsDependency object containing the API URL.
    :type settings: SettingsDependency
    :return: FileResponse object containing the event image.
    :rtype: FileResponse
    """

    response = requests.get(f"{settings.API_URL}/events/image/{image_uuid}")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to retrieve the image"
        )

    # Guardar la imagen en un archivo temporal
    content_type = response.headers.get("Content-Type", "")
    suffix = ".png"
    # Puedes agregar más tipos si lo necesitas

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(response.content)
    temp_file.close()

    filename = "image"
    content_disp = response.headers.get("Content-Disposition")
    if content_disp and "filename=" in content_disp:
        filename = content_disp.split("filename=")[1].strip('"')

    return FileResponse(
        temp_file.name,
        media_type=content_type,
        filename=filename,
        headers={"X-Accel-Buffering": "no"}
    )


@app.get(
    "/login",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the login page"
)
def login(
    request: Request,
    role: Annotated[str | None, Cookie()] = None
):
    """Endpoint to retrieve the login page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="login.html.j2",
        context={
            "request": request,
            "role": role,
        }
    )


@app.post(
    "/login",
    response_class=RedirectResponse,
    summary="Endpoint to handle login form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
def handle_login(
    form: Annotated[LoginForm, Form()],
    settings: SettingsDependency
):
    """Endpoint to handle login form submission.

    \f

    :param form: LoginForm object containing the form data.
    :type form: LoginForm
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = requests.post(
        f"{settings.API_URL}/token",
        data=form.model_dump()
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Credenciales inválidas"
        )

    token = response.json().get("access_token")
    # Obtener información del usuario usando el token
    user_response = requests.get(
        f"{settings.API_URL}/info",
        headers={"Authorization": f"Bearer {token}"}
    )

    if user_response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=user_response.status_code,
            detail="No se pudo obtener la información del usuario"
        )

    user_data = user_response.json()
    role = user_data.get("role")

    response = RedirectResponse(
        url="/home", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, secure=True)
    response.set_cookie(key="role", value=role)
    return response


@app.get(
    "/signup",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the signup page"
)
def signup(
    request: Request,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the signup page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="signup.html.j2",
        context={
            "request": request,
            "role": role,
        }
    )


@app.get(
    "/record-assistant/{event_id}/{event_date_id}",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the record assistant page"
)
async def record_assistant(
    request: Request,
    event_id: Annotated[int, Path()],
    event_date_id: Annotated[int, Path()],
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the record assistant page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="record_assistant.html.j2",
        context={
            "request": request,
            "event_id": event_id,
            "event_date_id": event_date_id,
            "role": role,
        }
    )


@app.get(
    "/settings",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the settings page"
)
async def settings(
    request: Request,
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the settings page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """
    app_settings = requests.get(f"{settings.API_URL}/organizer/get-settings")

    if app_settings.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=app_settings.status_code,
            detail="Error al obtener la configuración de la aplicación"
        )

    app_settings = app_settings.json()

    return templates.TemplateResponse(
        request=request,
        name="settings.html.j2",
        context={
            "request": request,
            "api_url": settings.API_URL,
            "app_settings": app_settings,
            "default_message": "",
            "role": role,
        }
    )


@app.post(
    "/record-assistant/{event_id}/{event_date_id}",
    response_class=HTMLResponse,
)
async def record_assistant_with_data(
    request: Request,
    image: Annotated[UploadFile, Form()],
    settings: SettingsDependency,
    event_id: Annotated[int, Path()],
    event_date_id: Annotated[int, Path()],
):
    """Endpoint to handle the recording of an assistant.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param image: Image file uploaded by the user.
    :type image: UploadFile
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """
    file = {
        "image": (image.filename, await image.read(), image.content_type)
    }

    assistants = requests.post(
        f"{settings.API_URL}/assistant/get-by-image?event_id={event_id}&event_date_id={event_date_id}",
        files=file  # type: ignore
    )

    assistants = assistants.json()

    # Verifica que si el json no es una lista, mandar una lista vacía
    if not isinstance(assistants, list):
        assistants = []

    return templates.TemplateResponse(
        request=request,
        name="record_assistant.html.j2",
        context={
            "request": request,
            "assistants": assistants,
            "event_id": event_id,
            "event_date_id": event_date_id,
            "api_url": settings.API_URL,
            "default_message": "No se puede reconocer el rostro o no coincide con ningún asistente registrado."
        }
    )


@app.get(
    "/events",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the events page"
)
async def events(
    request: Request,
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the events page with upcoming events.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.API_URL}/events/upcoming")

    events = response.json()

    if not events:
        events = []  # or handle the empty case as needed

    return templates.TemplateResponse(
        request=request,
        name="events.html.j2",
        context={
            "request": request,
            "events": events,
            "role": role,
        }
    )


@app.get(
    "/select-event-to-record",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the select event to record page"
)
async def select_event_to_record(
    request: Request,
    settings: SettingsDependency,
    access_token: Annotated[str, Cookie()],
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the select event to record page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/staff/my-events",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    events = response.json()

    if not events:
        events = []  # or handle the empty case as needed

    if not isinstance(events, list):
        events = []

    return templates.TemplateResponse(
        request=request,
        name="select_event_to_record.html.j2",
        context={
            "request": request,
            "events": events,
            "role": role
        }
    )


@app.get(
    "/event/detail/{event_id}",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the event detail page"
)
async def event_detail(
    request: Request,
    event_id: Annotated[
        int,
        Path(
            title="Event ID",
            description="The ID of the event to retrieve details for",
        )
    ],
    settings: SettingsDependency,
    access_token: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the event detail page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param event_id: ID of the event to retrieve details for.
    :type event_id: int
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """
    # Si no hay token debería redirigir a la página de login

    if not access_token:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/events/{event_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    event = response.json()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/assistant/get-registered-events",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        user_response = await client.get(
            f"{settings.API_URL}/assistant/info",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    registered_events_ids = []

    try:
        for registered_event in response.json():
            registered_events_ids.append(  # type: ignore
                registered_event["event_id"]
            )
    except TypeError:
        return RedirectResponse(
            "/all-events-view",
            status_code=status.HTTP_303_SEE_OTHER
        )

    role = None
    if user_response.status_code == status.HTTP_200_OK:
        role = user_response.json().get("role")

    user_info = user_response.json()
    return templates.TemplateResponse(
        request=request,
        name="event_detail.html.j2",
        context={
            "request": request,
            "event": event,
            "registered_events_ids": registered_events_ids,
            "role": role,
            "user_info": user_info
        }
    )


@app.get(
    "/edit-event/{event_id}",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the edit event page"
)
async def edit_event(
    request: Request,
    event_id: Annotated[
        int,
        Path(
            title="Event ID",
            description="The ID of the event to edit",
        )
    ],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the edit event page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param event_id: ID of the event to edit.
    :type event_id: int
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/events/{event_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    event = response.json()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_event.html.j2",
        context={
            "request": request,
            "event": event,
            "role": role,
        }
    )


@app.get(
    "/register-to/{event_id}",
    response_class=RedirectResponse,
    summary="Endpoint to register to an event",
    status_code=status.HTTP_303_SEE_OTHER
)
async def register_to_event(
    event_id: Annotated[
        int,
        Path(
            title="Event ID",
            description="The ID of the event to register to",
        )
    ],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to register to an event.

    \f

    :param event_id: ID of the event to register to.
    :type event_id: int
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = requests.post(
        f"{settings.API_URL}/assistant/register-to-event/{event_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return RedirectResponse(
        url="/events",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/unregister-to/{event_id}",
    response_class=RedirectResponse,
    summary="Endpoint to unregister from an event",
    status_code=status.HTTP_303_SEE_OTHER
)
async def unregister_from_event(
    event_id: Annotated[
        int,
        Path(
            title="Event ID",
            description="The ID of the event to unregister from",
        )
    ],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to unregister from an event.

    \f

    :param event_id: ID of the event to unregister from.
    :type event_id: int
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = requests.delete(
        f"{settings.API_URL}/assistant/unregister-from-event/{event_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return RedirectResponse(
        url="/events",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/add-companion/{event_id}",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the add companion page"
)
async def add_companion(
    request: Request,
    event_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to retrieve the add companion page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """
    response = requests.get(
        f"{settings.API_URL}/events/{event_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    event = response.json()

    return templates.TemplateResponse(
        request=request,
        name="add_companion.html.j2",
        context={
            "request": request,
            "event_id": event_id,
            "event": event
        }
    )


@app.get(
    "/profile",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the profile page"
)
async def profile(
    request: Request,
    settings: SettingsDependency,
    access_token: Annotated[str | None, Cookie()] = None,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the profile page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """
    if access_token is None:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/info",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        events_to_react = await client.get(
            f"{settings.API_URL}/events/events-to-react",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    if events_to_react.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=events_to_react.status_code,
            detail=events_to_react.text
        )

    events_to_react = events_to_react.json()

    if not events_to_react:
        events_to_react = []

    user = response.json()

    if user["role"] == "assistant":
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.API_URL}/assistant/info",
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user = response.json()

    return templates.TemplateResponse(
        request=request,
        name="user_profile.html.j2",
        context={
            "request": request,
            "user": user,
            "api_url": settings.API_URL,
            "events_to_react": events_to_react,
            "role": role,
        }
    )


@app.patch(
    "/profile",
    response_class=RedirectResponse,
    summary="Endpoint to handle profile partial update",
    status_code=status.HTTP_303_SEE_OTHER
)
@app.post(
    "/profile/update",
    response_class=RedirectResponse,
    summary="Endpoint to handle profile partial update via POST",
    status_code=status.HTTP_303_SEE_OTHER
)
async def update_profile(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to handle profile partial update.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: Redirect response to the profile page.
    :rtype: RedirectResponse
    """

    print(f"=== DEBUG UPDATE PROFILE START ===")
    print(f"Request method: {request.method}")
    print(f"Request URL: {request.url}")
    print(f"Request headers: {dict(request.headers)}")

    # Obtener los datos del formulario manualmente
    form_data = await request.form()

    print(f"Form data received: {dict(form_data)}")

    # Extraer datos del usuario
    user_data = {}
    if form_data.get("first_name"):
        user_data["first_name"] = form_data.get("first_name")
    if form_data.get("last_name"):
        user_data["last_name"] = form_data.get("last_name")
    if form_data.get("email"):
        user_data["email"] = form_data.get("email")
    if form_data.get("password"):
        user_data["password"] = form_data.get("password")

    # Extraer datos específicos del assistant
    assistant_data = {}
    if form_data.get("phone"):
        assistant_data["phone"] = form_data.get("phone")
    if form_data.get("id_number"):
        assistant_data["id_number"] = form_data.get("id_number")
    if form_data.get("gender"):
        assistant_data["gender"] = form_data.get("gender")
    if form_data.get("date_of_birth"):
        assistant_data["date_of_birth"] = form_data.get("date_of_birth")

    print(f"Extracted user_data: {user_data}")
    print(f"Extracted assistant_data: {assistant_data}")

    if not user_data and not assistant_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Al menos un campo debe ser proporcionado para actualizar"
        )

    # Obtener información del usuario para determinar el endpoint correcto
    user_info = await get_user_info(access_token, settings)
    if isinstance(user_info, RedirectResponse):
        return user_info

    user_id = user_info.get("id")
    user_role = user_info.get("role")

    print(f"User info: {user_info}")
    print(f"User ID: {user_id}, User Role: {user_role}")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo obtener el ID del usuario"
        )

    # Realizar la actualización según el rol
    response = await perform_profile_update(
        user_role, user_id, user_data, assistant_data, access_token, settings
    )

    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code not in [status.HTTP_200_OK]:
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        print(f"Error detail: {error_detail}")

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al actualizar perfil: {error_detail}"
        )

    print(f"=== DEBUG UPDATE PROFILE SUCCESS ===")
    return RedirectResponse(
        url="/profile",
        status_code=status.HTTP_303_SEE_OTHER
    )


async def get_user_info(access_token: str, settings):
    """Helper function to get user information."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/info",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener información del usuario"
        )

    return response.json()


async def perform_profile_update(
    user_role: str,
    user_id: int,
    user_data: dict,
    assistant_data: dict,
    access_token: str,
    settings
):
    """Helper function to perform the profile update based on user role."""
    print(f"=== DEBUG PROFILE UPDATE ===")
    print(f"User Role: {user_role}")
    print(f"User ID: {user_id}")
    print(f"User Data Raw: {user_data}")
    print(f"Assistant Data Raw: {assistant_data}")

    async with httpx.AsyncClient() as client:
        if user_role == "staff":
            update_url = f"{settings.API_URL}/staff/{user_id}"
            print(f"Staff Update URL: {update_url}")
            print(f"Staff Payload: {user_data}")
            return await client.patch(
                update_url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=user_data
            )
        elif user_role == "organizer":
            update_url = f"{settings.API_URL}/organizer/{user_id}"
            print(f"Organizer Update URL: {update_url}")
            print(f"Organizer Payload: {user_data}")
            return await client.patch(
                update_url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=user_data
            )
        elif user_role == "assistant":
            update_url = f"{settings.API_URL}/assistant/{user_id}"
            print(f"Assistant Update URL: {update_url}")

            # Validar los datos usando los modelos Pydantic antes de enviar
            try:
                from models.models import UserUpdate, AssistantUpdate
                import json
                from datetime import date

                print(f"Creating UserUpdate with data: {user_data}")
                print(f"Creating AssistantUpdate with data: {assistant_data}")

                # Crear instancias de los modelos para validación
                user_update_obj = UserUpdate(
                    **user_data) if user_data else UserUpdate()
                assistant_update_obj = AssistantUpdate(
                    **assistant_data) if assistant_data else AssistantUpdate()

                print(f"UserUpdate object created: {user_update_obj}")
                print(
                    f"AssistantUpdate object created: {assistant_update_obj}")

                # Convertir a diccionarios excluyendo valores no configurados
                user_update_dict = user_update_obj.model_dump(
                    exclude_unset=True)
                assistant_update_dict = assistant_update_obj.model_dump(
                    exclude_unset=True)

                print(f"UserUpdate dict: {user_update_dict}")
                print(f"AssistantUpdate dict: {assistant_update_dict}")

                # Convertir fechas a string ISO format si existen
                if 'date_of_birth' in assistant_update_dict and assistant_update_dict['date_of_birth']:
                    print(
                        f"Processing date_of_birth: {assistant_update_dict['date_of_birth']} (type: {type(assistant_update_dict['date_of_birth'])})")
                    if isinstance(assistant_update_dict['date_of_birth'], date):
                        assistant_update_dict['date_of_birth'] = assistant_update_dict['date_of_birth'].isoformat(
                        )
                        print(
                            f"Converted date_of_birth to: {assistant_update_dict['date_of_birth']}")

                # Crear el payload
                payload = {}
                if user_update_dict:
                    payload["user_update"] = user_update_dict
                if assistant_update_dict:
                    payload["assistant_update"] = assistant_update_dict

                print(f"Final payload: {payload}")
                print(f"Payload JSON: {json.dumps(payload, default=str)}")

                return await client.patch(
                    update_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

            except Exception as validation_error:
                print(f"Validation error: {str(validation_error)}")
                print(f"Error type: {type(validation_error)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                # Si hay un error de validación, manejarlo
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error de validación: {str(validation_error)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol de usuario no soportado para actualización"
            )


@app.delete(
    "/profile",
    summary="Endpoint to delete user profile",
)
async def delete_profile(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to delete user profile.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: JSON response or redirect response depending on request type.
    :rtype: dict | RedirectResponse
    """

    # Primero obtener información del usuario para determinar el endpoint correcto
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/info",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        # Si es una request AJAX/JavaScript, devolver JSON
        if request.headers.get("accept") == "application/json":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autorizado"
            )
        # Si es una request normal, redireccionar
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener información del usuario"
        )

    user_info = response.json()
    user_id = user_info.get("id")
    user_role = user_info.get("role")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo obtener el ID del usuario"
        )

    # Determinar el endpoint basado en el rol del usuario
    if user_role == "staff":
        delete_url = f"{settings.API_URL}/staff/{user_id}"
    elif user_role == "organizer":
        delete_url = f"{settings.API_URL}/organizer/{user_id}"
    elif user_role == "assistant":
        # Para assistants, necesitamos usar un endpoint diferente si existe
        delete_url = f"{settings.API_URL}/assistant/{user_id}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol de usuario no soportado para eliminación"
        )

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        # Si es una request AJAX/JavaScript, devolver JSON
        if request.headers.get("accept") == "application/json":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autorizado"
            )
        # Si es una request normal, redireccionar
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]:
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al eliminar perfil: {error_detail}"
        )

    # Si es una request AJAX/JavaScript, devolver JSON de éxito
    if request.headers.get("accept") == "application/json":
        # También limpiar las cookies al eliminar el perfil
        response = {"message": "Perfil eliminado con éxito"}
        return response

    # Si es una request normal, redireccionar al logout para limpiar cookies
    return RedirectResponse(
        url="/logout",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/create-staff",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the create staff page"
)
async def create_staff(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the create staff page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="add_staff.html.j2",
        context={
            "request": request,
            "role": role,
        }
    )


@app.post(
    "/create-staff",
    response_class=RedirectResponse,
    summary="Endpoint to handle create staff form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_create_staff(
    form: Annotated[
        Staff,
        Form()
    ],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
):
    """Endpoint to handle create staff form submission.

    \f

    :param form: Staff object containing the form data.
    :type form: Staff
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = requests.post(
        f"{settings.API_URL}/staff/add",
        headers={"Authorization": f"Bearer {access_token}"},
        data=form.model_dump()
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return RedirectResponse(
        url="/staff",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/staff",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the staff management page"
)
async def staff_list(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the staff management page with all staff members.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/staff/all",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener la lista de staff"
        )

    staff_members = response.json()

    return templates.TemplateResponse(
        request=request,
        name="staff.html.j2",
        context={
            "request": request,
            "staff_members": staff_members,
            "api_url": settings.API_URL,
            "role": role,
        }
    )


@app.get(
    "/staff/edit/{staff_id}",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the edit staff page"
)
async def edit_staff_form(
    request: Request,
    staff_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the edit staff page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param staff_id: ID of the staff member to edit.
    :type staff_id: int
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        # Obtener información del staff específico
        response = await client.get(
            f"{settings.API_URL}/staff/all",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener la información del staff"
        )

    all_staff = response.json()
    staff_member = next(
        (staff for staff in all_staff if staff["id"] == staff_id), None)

    if not staff_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_staff.html.j2",
        context={
            "request": request,
            "staff_member": staff_member,
            "role": role,
        }
    )


@app.post(
    "/staff/update/{staff_id}",
    response_class=RedirectResponse,
    summary="Endpoint to handle staff update",
    status_code=status.HTTP_303_SEE_OTHER
)
async def update_staff(
    request: Request,
    staff_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to handle staff update.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param staff_id: ID of the staff member to update.
    :type staff_id: int
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: Redirect response to the staff page.
    :rtype: RedirectResponse
    """

    # Obtener los datos del formulario
    form_data = await request.form()

    # Extraer datos para actualización
    user_data = {}
    if form_data.get("first_name"):
        user_data["first_name"] = form_data.get("first_name")
    if form_data.get("last_name"):
        user_data["last_name"] = form_data.get("last_name")
    if form_data.get("email"):
        user_data["email"] = form_data.get("email")
    if form_data.get("password") and form_data.get("password").strip():
        user_data["password"] = form_data.get("password")

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Al menos un campo debe ser proporcionado para actualizar"
        )

    # Crear instancia del modelo para validación
    try:
        user_update_obj = UserUpdate(**user_data)
        user_update_dict = user_update_obj.model_dump(exclude_unset=True)
    except Exception as validation_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {str(validation_error)}"
        )

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.API_URL}/staff/{staff_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json=user_update_dict
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al actualizar staff: {error_detail}"
        )

    return RedirectResponse(
        url="/staff",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.delete(
    "/staff/delete/{staff_id}",
    summary="Endpoint to delete staff member"
)
async def delete_staff(
    request: Request,
    staff_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to delete staff member.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param staff_id: ID of the staff member to delete.
    :type staff_id: int
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: JSON response or redirect response depending on request type.
    :rtype: dict | RedirectResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.API_URL}/staff/{staff_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        # Si es una request AJAX/JavaScript, devolver JSON
        if request.headers.get("accept") == "application/json":
            return {"error": "Unauthorized", "redirect": "/login"}
        # Si es una request normal, redireccionar
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]:
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        if request.headers.get("accept") == "application/json":
            return {"error": f"Error al eliminar staff: {error_detail}"}

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al eliminar staff: {error_detail}"
        )

    # Si es una request AJAX/JavaScript, devolver JSON de éxito
    if request.headers.get("accept") == "application/json":
        return {"message": "Staff eliminado con éxito"}

    # Si es una request normal, redireccionar
    return RedirectResponse(
        url="/staff",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/organizer",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the organizers management page"
)
async def organizer_list(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the organizers management page with all organizers.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/organizer/all",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener la lista de organizadores"
        )

    organizers = response.json()

    return templates.TemplateResponse(
        request=request,
        name="organizer.html.j2",
        context={
            "request": request,
            "organizers": organizers,
            "api_url": settings.API_URL,
            "role": role,
        }
    )


@app.get(
    "/create-organizer",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the create organizer page"
)
async def create_organizer(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to retrieve the create organizer page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="add_organizer.html.j2",
        context={
            "request": request,
        }
    )


# @app.post(
#     "/create-organizer",
#     response_class=RedirectResponse,
#     summary="Endpoint to handle create organizer form submission",
#     status_code=status.HTTP_303_SEE_OTHER
# )
# async def handle_create_organizer(
#     form: Annotated[
#         Staff,
#         Form()
#     ],
#     access_token: Annotated[str, Cookie()],
#     settings: SettingsDependency
# ):
#     """Endpoint to handle create organizer form submission.

#     \f

#     :param form: Staff object containing the form data.
#     :type form: Staff
#     :return: Redirect response to the home page.
#     :rtype: RedirectResponse
#     """

#     response = requests.post(
#         f"{settings.API_URL}/organizer/add",
#         headers={"Authorization": f"Bearer {access_token}"},
#         data=form.model_dump()
#     )

#     if response.status_code == status.HTTP_401_UNAUTHORIZED:
#         return RedirectResponse(
#             url="/login",
#             status_code=status.HTTP_303_SEE_OTHER
#         )

#     if response.status_code != status.HTTP_201_CREATED:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=response.text
#         )

#     return RedirectResponse(
#         url="/home",
#         status_code=status.HTTP_303_SEE_OTHER
#     )


@app.post(
    "/create-organizer",
    response_class=RedirectResponse,
    summary="Endpoint to handle create organizer form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_create_organizer(
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to handle create organizer form submission.

    \f

    :param first_name: First name of the organizer.
    :type first_name: str
    :param last_name: Last name of the organizer.
    :type last_name: str
    :param email: Email of the organizer.
    :type email: str
    :param password: Password of the organizer.
    :type password: str
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: Redirect response to the organizer page.
    :rtype: RedirectResponse
    """

    organizer_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }

    response = requests.post(
        f"{settings.API_URL}/organizer/add",
        headers={"Authorization": f"Bearer {access_token}"},
        data=organizer_data
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return RedirectResponse(
        url="/organizer",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/logout",
    response_class=RedirectResponse,
    summary="Endpoint to handle logout",
    status_code=status.HTTP_303_SEE_OTHER
)
async def logout():
    """Endpoint to handle logout.

    \f

    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = RedirectResponse(
        url="/home", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="role")
    return response


# @app.get(
#     "/organizer",
#     response_class=HTMLResponse,
#     summary="Página del organizador con sus eventos"
# )
# async def organizer(
#     request: Request,
#     access_token: Annotated[str, Cookie()] = None,
#     settings: SettingsDependency = None
# ):
#     """Página que muestra todos los usuarios organizadores."""
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"{settings.API_URL}/organizer/all",
#             headers={
#                 "Authorization": f"Bearer {access_token}"} if access_token else None
#         )

#     organizers = response.json() or []
#     return templates.TemplateResponse(
#         "organizer.html.j2",
#         {
#             "request": request,
#             "organizers": organizers
#         }
#     )


@app.get(
    "/edit-organizer/{organizer_id}",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the edit organizer page"
)
async def edit_organizer_form(
    request: Request,
    organizer_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to retrieve the edit organizer page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param organizer_id: ID of the organizer to edit.
    :type organizer_id: int
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        # Primero obtenemos todos los organizadores
        response = await client.get(
            f"{settings.API_URL}/organizer/all",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener los datos del organizador"
        )

    organizers = response.json()

    # Buscamos el organizador específico por ID
    organizer = None
    for org in organizers:
        if org.get("id") == organizer_id:
            organizer = org
            break

    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizador no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_organizer.html.j2",
        context={
            "request": request,
            "organizer": organizer,
            "organizer_id": organizer_id
        }
    )


@app.post(
    "/edit-organizer/{organizer_id}",
    response_class=RedirectResponse,
    summary="Endpoint to handle edit organizer form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_edit_organizer(
    organizer_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    first_name: Annotated[str, Form()] = "",
    last_name: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    password: Annotated[str, Form()] = ""
):
    """Endpoint to handle edit organizer form submission.

    \f

    :param organizer_id: ID of the organizer to edit.
    :type organizer_id: int
    :param first_name: First name of the organizer.
    :type first_name: str
    :param last_name: Last name of the organizer.
    :type last_name: str
    :param email: Email of the organizer.
    :type email: str
    :param password: Password of the organizer.
    :type password: str
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: Redirect response to the organizer page.
    :rtype: RedirectResponse
    """

    # Crear datos solo con campos no vacíos
    organizer_data = {}
    if first_name:
        organizer_data["first_name"] = first_name
    if last_name:
        organizer_data["last_name"] = last_name
    if email:
        organizer_data["email"] = email
    if password:
        organizer_data["password"] = password

    if not organizer_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un campo para actualizar"
        )

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.API_URL}/organizer/{organizer_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json=organizer_data
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al actualizar el organizador"
        )

    return RedirectResponse(
        url="/organizer",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.delete(
    "/delete-organizer/{organizer_id}",
    summary="Endpoint to delete an organizer"
)
async def delete_organizer(
    request: Request,
    organizer_id: Annotated[int, Path()],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to delete an organizer.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param organizer_id: ID of the organizer to delete.
    :type organizer_id: int
    :param access_token: Access token from cookie.
    :type access_token: str
    :param settings: Application settings.
    :type settings: SettingsDependency
    :return: JSON response or redirect response depending on request type.
    :rtype: dict | RedirectResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.API_URL}/organizer/{organizer_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        # Si es una request AJAX/JavaScript, devolver JSON
        if request.headers.get("accept") == "application/json":
            return {"error": "Unauthorized", "redirect": "/login"}
        # Si es una request normal, redireccionar
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]:
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        if request.headers.get("accept") == "application/json":
            return {"error": f"Error al eliminar organizador: {error_detail}"}

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al eliminar organizador: {error_detail}"
        )

    # Si es una request AJAX/JavaScript, devolver JSON de éxito
    if request.headers.get("accept") == "application/json":
        return {"message": "Organizador eliminado con éxito"}

    # Si es una request normal, redireccionar
    return RedirectResponse(
        url="/organizer",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/create-event",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the create event page"
)
async def create_event_page(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the create event page.

    \\f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    # Check if the user is an organizer
    # This is a placeholder, replace with actual logic to check user role
    # For example, decode the access_token or call an API endpoint

    return templates.TemplateResponse(
        request=request,
        name="add_event.html.j2",
        context={
            "request": request,
            "role": role,
        }
    )


@app.post(
    "/create-event",
    response_class=RedirectResponse,
    summary="Endpoint to handle create event form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_create_event(
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    location: Annotated[str, Form()],
    maps_link: Annotated[str, Form()],
    capacity: Annotated[int, Form()],
    capacity_type: Annotated[str, Form()],
    image: Annotated[UploadFile, File()]
):
    """Endpoint to handle create event form submission.

    \\f

    :param name: Event name.
    :type name: str
    :param description: Event description.
    :type description: str
    :param location: Event location.
    :type location: str
    :param maps_link: Event maps link.
    :type maps_link: str
    :param capacity: Event maximum capacity.
    :type capacity: int
    :param capacity_type: Type of capacity for the event.
    :type capacity_type: str
    :param image: Path to event image.
    :type image: UploadFile
    :return: Redirect response to the events page.
    :rtype: RedirectResponse
    """
    event_data = {
        "name": name,
        "description": description,
        "location": location,
        "maps_link": maps_link,
        "capacity": capacity,
        "capacity_type": capacity_type,
    }
    files = {"image": (image.filename, image.file, image.content_type)}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.API_URL}/events/add",
            headers={"Authorization": f"Bearer {access_token}"},
            data=event_data,
            files=files
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return RedirectResponse(
        url="/all-events-view",  # Or perhaps a detail page for the newly created event
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/all-events-view",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the all events view page"
)
async def all_events_view(
    request: Request,
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None
):
    """Endpoint to retrieve the all events view page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.API_URL}/events/all")

    events = response.json()

    if not events:
        events = []

    if not isinstance(events, list):
        events = []

    return templates.TemplateResponse(
        request=request,
        name="all_events_view.html.j2",
        context={
            "request": request,
            "events": events,
            "role": role,
        }
    )


@app.get(
    "/staff",
    response_class=HTMLResponse,
    summary="Página de staff con todos los usuarios staff"
)
async def staff(
    request: Request,
    access_token: Annotated[str, Cookie()] = None,
    settings: SettingsDependency = None
):
    """Página de staff con todos los usuarios staff."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/users/staff",
            headers={
                "Authorization": f"Bearer {access_token}"} if access_token else None
        )

        response = await client.get(
            f"{settings.API_URL}/staff/all",
            headers={
                "Authorization": f"Bearer {access_token}"} if access_token else None
        )
    organizers = response.json() if response.status_code == 200 else []
    return templates.TemplateResponse(
        request=request,
        name="staff.html.j2",
        context={
            "request": request,
            "organizers": organizers
        }
    )


@app.get(
    "/{event_id}/event-dates",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the event dates page"
)
async def event_dates_view(
    request: Request,
    event_id: int,
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the event dates page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param event_id: ID of the event to retrieve dates for.
    :type event_id: int
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.API_URL}/events/{event_id}/dates")

    event_dates = response.json()

    return templates.TemplateResponse(
        request=request,
        name="event_dates_view.html.j2",
        context={
            "request": request,
            "event_dates": event_dates,
            "event_id": event_id,
            "role": role,
        }
    )


# /{{ event_id }}/create-date
@app.get(
    "/{event_id}/create-date",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the create event date page"
)
async def create_event_date_page(
    request: Request,
    event_id: int,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the create event date page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param event_id: ID of the event to create a date for.
    :type event_id: int
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    return templates.TemplateResponse(
        request=request,
        name="add_event_date.html.j2",
        context={
            "request": request,
            "event_id": event_id,
            "role": role,
        }
    )


@app.post(
    "/{event_id}/create-date",
    response_class=RedirectResponse,
    summary="Endpoint to handle create event date form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_create_event_date(
    request: Request,
    event_id: int,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    day_date: Annotated[str, Form()],
    start_time: Annotated[str, Form()],
    end_time: Annotated[str, Form()],
):
    """Endpoint to handle create event date form submission.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :param event_id: ID of the event to create a date for.
    :type event_id: int
    :param day_date: Date of the event date.
    :type day_date: str
    :param start_time: Start time of the event date.
    :type start_time: str
    :param end_time: End time of the event date.
    :type end_time: str
    :return: Redirect response to the event dates page.
    :rtype: RedirectResponse
    """

    data = {
        "day_date": day_date,
        "start_time": start_time,
        "end_time": end_time,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.API_URL}/events/{event_id}/date/add",
            headers={"Authorization": f"Bearer {access_token}"},
            data=data
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return RedirectResponse(
        url=f"/{event_id}/event-dates",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/staff-to-event",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the add staff to event page"
)
async def add_staff_to_event_page(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency,
    role: Annotated[str | None, Cookie()] = None,
):
    """Endpoint to retrieve the add staff to event page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    # Envía todos los staff al template y también todos los eventos
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/staff/all",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    staff = response.json()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/events/upcoming",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    events = response.json()

    return templates.TemplateResponse(
        request=request,
        name="add_staff_to_event.html.j2",
        context={
            "request": request,
            "staff_list": staff,
            "events_list": events,
            "role": role,
        }
    )
