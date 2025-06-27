// // static/js/organizer_operations.js

// // Base URL de tu API (mismo host y puerto que en eventos)
// const API_URL = "http://127.0.0.1:8000/organizer";

/**
 * Elimina un organizador por su ID.
 * @param {number} organizerId
 */
function deleteOrganizer(organizerId) {
    if (!confirm("¿Estás seguro de que deseas eliminar este organizador?")) {
        return;
    }

    fetch(`${API_URL}/organizer/${organizerId}`, {
        method: "DELETE",
        headers: {
            accept: "application/json",
        },
    })
    .then((response) => {
        if (response.ok) {
            alert("Organizador eliminado con éxito");
            location.reload();
        } else {
            return response.json().then((data) => {
                throw new Error(data.detail || "Error al eliminar el organizador");
            });
        }
    })
    .catch((error) => {
        alert("Error: " + error.message);
    });
}


document.getElementById("login-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    // Elimina el campo confirm_password antes de enviar
    formData.delete("confirm_password");

    fetch("/create-organizer", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (response.redirected) {
                window.location.href = response.url;
            } else if (!response.ok) {
                return response.text().then((errorText) => {
                    alert("Error en el registro: " + errorText);
                });
            }
        })
        .catch((err) => {
            alert("Error de red: " + err.message);
        });
});