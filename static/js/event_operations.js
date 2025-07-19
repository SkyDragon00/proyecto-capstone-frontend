function deleteEvent(eventId) {
    // Ask for confirmation before deleting
    if (!confirm("¿Estás seguro de que deseas eliminar este evento?")) {
        return;
    }

    fetch(`${API_URL}/events/${eventId}`, {
        method: "DELETE",
        headers: {
            accept: "application/json",
        },
    })
        .then((response) => {
            if (response.ok) {
                alert("Evento eliminado con éxito");
                // Reload the page to reflect the changes
                location.reload();
            } else {
                return response.json().then((data) => {
                    throw new Error(
                        data.detail || "Error al eliminar el evento"
                    );
                });
            }
        })
        .catch((error) => alert("Error: " + error.message));
}

function deleteDate(dateId) {
    // Ask for confirmation before deleting
    if (!confirm("¿Estás seguro de que deseas eliminar esta fecha?")) {
        return;
    }

    fetch(`${API_URL}/events/date/${dateId}`, {
        method: "DELETE",
        headers: {
            accept: "application/json",
        },
    })
        .then((response) => {
            if (response.ok) {
                alert("Fecha eliminada con éxito");
                // Reload the page to reflect the changes
                location.reload();
            } else {
                return response.json().then((data) => {
                    throw new Error(
                        data.detail || "Error al eliminar la fecha"
                    );
                });
            }
        })
        .catch((error) => alert("Error: " + error.message));
}
