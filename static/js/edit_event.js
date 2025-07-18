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
        alert("Por favor, complete todos los campos.");
        event.preventDefault();
        return;
    }

    if (!mapsLink.startsWith("https://maps.app.goo.gl/")) {
        alert(
            'El enlace de Google Maps debe comenzar con "https://maps.app.goo.gl/"'
        );
        event.preventDefault();
        return;
    }

    const formData = new FormData(document.getElementById("event-form"));

    fetch(`https://proyecto-capstone-backend.onrender.com/events/${eventId}`, {
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

    fetch(
        `https://proyecto-capstone-backend.onrender.com/events/${eventId}/image`,
        {
            method: "PATCH",
            body: formData,
        }
    ).then((response) => {
        if (response.ok) {
            alert("Imagen del evento editada con éxito");
            window.location.reload();
        } else {
            alert("Error al editar la imagen del evento");
        }
    });
}
