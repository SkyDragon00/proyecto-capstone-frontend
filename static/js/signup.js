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
                return response.json().then((errorText) => {
                    if (
                        errorText["detail"].includes(
                            "Face could not be detected"
                        )
                    ) {
                        alert(
                            "No se pudo detectar un único rostro en la imagen. Por favor, asegúrate de que la imagen contenga un solo rostro claro y visible."
                        );
                    } else {
                        alert("Error en el registro: " + errorText.detail);
                    }
                });
            }
        })
        .catch((err) => {
            alert("Error de red: " + err.message);
        });
});
