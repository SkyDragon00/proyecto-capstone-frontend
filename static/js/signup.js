document.getElementById("login-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    // Elimina el campo confirm_password antes de enviar
    formData.delete("confirm_password");

    fetch("http://127.0.0.1:8000/assistant/add", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (response.ok) {
                window.location.href = "/login";
            } else {
                return response.text().then((errorText) => {
                    alert("Error en el registro: " + errorText);
                });
            }
        })
        .catch((err) => {
            alert("Error de red: " + err.message);
        });
});
