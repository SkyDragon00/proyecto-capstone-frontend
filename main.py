from typing import Annotated
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel
import requests

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
async def login(request: Request):
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


@app.post(
    "/login",
    response_class=RedirectResponse,
    summary="Endpoint to handle login form submission"
)
async def handle_login(
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
        response = RedirectResponse(
            url="/home",
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
