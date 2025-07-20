function editEvent(eventId) {
    const event = document.getElementById("event-form");
    const name = document.getElementById("name").value.trim();
    const description = document.getElementById("description").value.trim();
    const location = document.getElementById("location").value.trim();
    const mapsLink = document.getElementById("maps_link").value.trim();
    const capacity = document.getElementById("capacity").value.trim();
    const capacityType = document.getElementById("capacity_type").value;

    if (
        !name ||
        !description ||
        !location ||
        !mapsLink ||
        !capacity ||
        !capacityType
    ) {
        Swal.fire({
            title: "Campos incompletos",
            text: "Por favor, complete todos los campos.",
            icon: "warning",
            confirmButtonText: "Entendido",
        });
        event.preventDefault();
        return;
    }

    if (!mapsLink.startsWith("https://maps.app.goo.gl/")) {
        Swal.fire({
            title: "Enlace inválido",
            text: 'El enlace de Google Maps debe comenzar con "https://maps.app.goo.gl/"',
            icon: "error",
            confirmButtonText: "Entendido",
        });
        event.preventDefault();
        return;
    }

    const formData = new FormData(document.getElementById("event-form"));

    fetch(`${API_URL}/events/${eventId}`, {
        method: "PATCH",
        // Envía como JSON
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: {
            "Content-Type": "application/json",
        },
    }).then((response) => {
        if (response.ok) {
            Swal.fire({
                title: "Evento editado",
                text: "Evento editado con éxito",
                icon: "success",
                confirmButtonText: "OK",
            }).then(() => {
                window.location.reload();
            });
        } else {
            Swal.fire({
                title: "Error",
                text: "Error al editar el evento",
                icon: "error",
                confirmButtonText: "Intentar de nuevo",
            });
        }
    });
}

function editImageEvent(eventId) {
    const formData = new FormData(document.getElementById("event-img-form"));

    fetch(`${API_URL}/events/${eventId}/image`, {
        method: "PATCH",
        body: formData,
    }).then((response) => {
        if (response.ok) {
            Swal.fire({
                title: "Imagen editada",
                text: "Imagen del evento editada con éxito",
                icon: "success",
                confirmButtonText: "OK",
            }).then(() => {
                window.location.reload();
            });
        } else {
            Swal.fire({
                title: "Error",
                text: "Error al editar la imagen del evento",
                icon: "error",
                confirmButtonText: "Intentar de nuevo",
            });
        }
    });
}
