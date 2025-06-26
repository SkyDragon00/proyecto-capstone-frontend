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