async function deleteEvent(eventId) {
    // Ask for confirmation before deleting
    const result = await Swal.fire({
        title: "¿Estás seguro?",
        text: "¿Estás seguro de que deseas eliminar este evento?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
    });

    if (!result.isConfirmed) {
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
                Swal.fire({
                    title: "Evento eliminado",
                    text: "Evento eliminado con éxito",
                    icon: "success",
                    confirmButtonText: "OK",
                }).then(() => {
                    // Reload the page to reflect the changes
                    location.reload();
                });
            } else {
                return response.json().then((data) => {
                    throw new Error(
                        data.detail || "Error al eliminar el evento"
                    );
                });
            }
        })
        .catch((error) => {
            Swal.fire({
                title: "Error",
                text: "Error: " + error.message,
                icon: "error",
                confirmButtonText: "Entendido",
            });
        });
}

async function deleteDate(dateId) {
    // Ask for confirmation before deleting
    const result = await Swal.fire({
        title: "¿Estás seguro?",
        text: "¿Estás seguro de que deseas eliminar esta fecha?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
    });

    if (!result.isConfirmed) {
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
                Swal.fire({
                    title: "Fecha eliminada",
                    text: "Fecha eliminada con éxito",
                    icon: "success",
                    confirmButtonText: "OK",
                }).then(() => {
                    // Reload the page to reflect the changes
                    location.reload();
                });
            } else {
                return response.json().then((data) => {
                    throw new Error(
                        data.detail || "Error al eliminar la fecha"
                    );
                });
            }
        })
        .catch((error) => {
            Swal.fire({
                title: "Error",
                text: "Error: " + error.message,
                icon: "error",
                confirmButtonText: "Entendido",
            });
        });
}
