function editEvent(eventId) {
    const formData = new FormData(document.getElementById("event-form"));

    fetch(`http://127.0.0.1:8000/events/${eventId}`, {
        method: "PATCH",
        // Envía como JSON
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: {
            "Content-Type": "application/json",
        },
    }).then((response) => {
        if (response.ok) {
            alert("Evento editado con éxito");
            window.location.reload();
        } else {
            alert("Error al editar el evento");
        }
    });
}

function editImageEvent(eventId) {
    const formData = new FormData(document.getElementById("event-img-form"));

    fetch(`http://127.0.0.1:8000/events/${eventId}/image`, {
        method: "PATCH",
        body: formData,
    }).then((response) => {
        if (response.ok) {
            alert("Imagen del evento editada con éxito");
            window.location.reload();
        } else {
            alert("Error al editar la imagen del evento");
        }
    });
}
