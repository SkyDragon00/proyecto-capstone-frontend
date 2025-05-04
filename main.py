from typing import Annotated
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import requests

from models.models import LoginForm, SignupForm

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get(
    "/home",
    response_class=HTMLResponse,
    summary="Endpoint to retrieve the home page"
)
async def home(request: Request):
    """Endpoint to retrieve the home page with upcoming events.

    \f

    :param request: Request object containing request information.
    :type request: Request
    :return: HTML response with the rendered template.
    :rtype: _TemplateResponse
    """

    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/events/upcoming?quantity=3")

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
    form: Annotated[LoginForm, Form()]
):
    """Endpoint to handle login form submission.

    \f

    :param form: LoginForm object containing the form data.
    :type form: LoginForm
    :return: Redirect response to the home page.
    :rtype: RedirectResponse
    """

    response = requests.post(
        "http://127.0.0.1:8000/token",
        data=form.model_dump()
    )

    if response.status_code == status.HTTP_200_OK:
        token = response.json().get("access_token")
        # Store the token in a session or cookie as needed
        # For example, using a cookie:
        response = RedirectResponse(url="/home")
        response.set_cookie(key="access_token", value=token, httponly=True)
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
        "http://127.0.0.1:8000/assistant/add",
        data=form.model_dump(),
        files=files  # type: ignore
    )
    print(response.json())
    if response.status_code == status.HTTP_201_CREATED:
        return "/login"
