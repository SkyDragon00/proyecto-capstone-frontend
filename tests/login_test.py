import re
from playwright.sync_api import Page, expect

def test_login_and_redirects_to_home(page: Page):
    # 1. Navegamos a la URL de login
    page.goto("http://localhost:8000/login")
    page.wait_for_selector('form#login-form')
    page.get_by_label("Email:").fill("dome62832+4@gmail.com")
    page.get_by_label("Contraseña:").fill("Hola1234@")

    # 3. Pulsamos el botón con texto exacto "Iniciar Sesión"
    page.get_by_role("button", name="Iniciar Sesión").click()

    # 4. Esperamos a que la URL cambie a /home (puede tardar un momento).
    #    Aquí usamos expect().to_have_url, que internamente reintenta hasta que
    #    coincida o se agote el timeout por defecto.
    expect(page).to_have_url(re.compile(r".*/home$"))

    # 5. Verificamos que en “/home” haya algún elemento visible que
    #    confirme que estamos en la página correcta. Ajusta el selector/texto
    #    a lo que realmente muestre tu home (por ejemplo un <h1> "Bienvenido").
    #    En este ejemplo buscaremos cualquier texto “Bienvenido” o “Home”.
    expect(page.get_by_text(re.compile(r"Bienvenido|Home", re.IGNORECASE))).to_be_visible()
