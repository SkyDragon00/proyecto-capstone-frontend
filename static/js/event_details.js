// Crea un event listener para cuando le den click a este botón saque una alerta register-button
document
    .getElementById("register-button")
    .addEventListener("click", function (event) {
        document.getElementById("pardot-form").submit();
    });
