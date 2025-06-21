import tempfile
from typing import Annotated
from uuid import UUID
from fastapi import Cookie, FastAPI, Form, HTTPException, Path, Request, UploadFile, File, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import requests

from config import SettingsDependency
from models.models import LoginForm, Staff
from datetime import datetime

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
async def home(request: Request, settings: SettingsDependency):
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
            "events": events
        }
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
def login(request: Request):
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
            "request": request
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

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Credenciales inválidas"
        )

    print(response.json())
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
    response.set_cookie(key="access_token", value=token,
                        httponly=True, secure=True)
    response.set_cookie(key="role", value=role, httponly=True)
    return response


@app.get(
    "/signup",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the signup page"
)
def signup(
    request: Request,
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
            "request": request
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

    return templates.TemplateResponse(
        request=request,
        name="record_assistant.html.j2",
        context={
            "request": request,
            "assistants": assistants,
            "event_id": event_id,
            "event_date_id": event_date_id,
            "api_url": settings.API_URL
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
            "events": events
        }
    )


@app.get(
    "/select-event-to-record",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the select event to record page"
)
async def select_event_to_record(
    request: Request,
    settings: SettingsDependency
):
    """Endpoint to retrieve the select event to record page.

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
        name="select_event_to_record.html.j2",
        context={
            "request": request,
            "events": events
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
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
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
            f"{settings.API_URL}/info",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    registered_events_ids = []

    for registered_event in response.json():
        registered_events_ids.append(  # type: ignore
            registered_event["event_id"]
        )

    role = None
    if user_response.status_code == status.HTTP_200_OK:
        role = user_response.json().get("role")

    return templates.TemplateResponse(
        request=request,
        name="event_detail.html.j2",
        context={
            "request": request,
            "event": event,
            "registered_events_ids": registered_events_ids,
            "role": role
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
    "/profile",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the profile page"
)
async def profile(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to retrieve the profile page.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

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
            detail=response.text
        )

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
            "api_url": settings.API_URL
        }
    )


@app.get(
    "/create-staff",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the create staff page"
)
async def create_staff(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
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
    settings: SettingsDependency
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
        url="/home",
        status_code=status.HTTP_303_SEE_OTHER
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


@app.post(
    "/create-organizer",
    response_class=RedirectResponse,
    summary="Endpoint to handle create organizer form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_create_organizer(
    form: Annotated[
        Staff,
        Form()
    ],
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
):
    """Endpoint to handle create organizer form submission.

    \f

    :param form: Staff object containing the form data.
    :type form: Staff
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = requests.post(
        f"{settings.API_URL}/organizer/add",
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
        url="/home",
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


@app.get(
    "/organizer",
    response_class=HTMLResponse,
    summary="Página del organizador con sus eventos"
)
async def organizer(
    request: Request,
    access_token: Annotated[str, Cookie()] = None,
    settings: SettingsDependency = None
):
    """Página que muestra todos los usuarios organizadores."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_URL}/organizer", 
            headers={"Authorization": f"Bearer {access_token}"} if access_token else None
        )

        response = await client.get(
            f"{settings.API_URL}/organizer/all",
            headers={"Authorization": f"Bearer {access_token}"} if access_token else None
        )

    organizers = response.json() or []
    return templates.TemplateResponse(
        "organizer.html.j2",
        {
            "request": request,
            "organizers": organizers
        }
    )


@app.get(
    "/create-event",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the create event page"
)
async def create_event_page(
    request: Request,
    access_token: Annotated[str, Cookie()],
    settings: SettingsDependency
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
        url="/events",  # Or perhaps a detail page for the newly created event
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get(
    "/all-events-view",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the all events view page"
)
async def all_events_view(
    request: Request,
    settings: SettingsDependency
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

    return templates.TemplateResponse(
        request=request,
        name="all_events_view.html.j2",
        context={
            "request": request,
            "events": events
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
            headers={"Authorization": f"Bearer {access_token}"} if access_token else None
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
    settings: SettingsDependency
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
    settings: SettingsDependency
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
    end_time: Annotated[str, Form()]
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
    settings: SettingsDependency
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
            "events_list": events
        }
    )
