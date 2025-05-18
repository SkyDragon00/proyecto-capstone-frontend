import tempfile
from typing import Annotated
from uuid import UUID
from fastapi import Cookie, FastAPI, Form, HTTPException, Path, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import requests

from config import SettingsDependency
from models.models import LoginForm, SignupForm

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


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
def signup(request: Request):
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


@app.post(
    "/signup",
    response_class=RedirectResponse,
    summary="Endpoint to handle signup form submission",
    status_code=status.HTTP_303_SEE_OTHER
)
async def handle_signup(
    form: Annotated[
        SignupForm,
        Form(
            media_type="multipart/form-data",
        )
    ],
    settings: SettingsDependency
):
    """Endpoint to handle signup form submission.

    \f

    :param form: SignupForm object containing the form data.
    :type form: SignupForm
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    files = {
        "image": (form.image.filename, await form.image.read(), form.image.content_type)
    }

    response = requests.post(
        f"{settings.API_URL}/assistant/add",
        data=form.model_dump(),
        files=files  # type: ignore
    )
    print(response.json())
    if response.status_code == status.HTTP_201_CREATED:
        return "/login"


@app.get(
    "/record-assistant",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the record assistant page"
)
async def record_assistant(
    request: Request,
    role: Annotated[str, Cookie()]
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
            "request": request
        }
    )


@app.post(
    "/record-assistant",
    response_class=HTMLResponse,
)
async def record_assistant_with_data(
    request: Request,
    image: Annotated[UploadFile, Form()],
    settings: SettingsDependency,
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

    response = requests.post(
        f"{settings.API_URL}/assistant/get-by-image",
        files=file  # type: ignore
    )

    assistants = response.json()

    return templates.TemplateResponse(
        request=request,
        name="record_assistant.html.j2",
        context={
            "request": request,
            "assistants": assistants,
            "api_url": settings.API_URL
        }
    )
