function addStaffToEvent() {
    const staffId = document.getElementById("staff-id").value;
    const eventId = document.getElementById("event-id").value;

    if (!staffId) {
        alert("Por favor, selecciona un miembro del personal.");
        return;
    }

    fetch(`http://127.0.0.1:8000/staff/add-staff-to-event`, {
        method: "POST",
        headers: {
            accept: "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `staff_id=${staffId}&event_id=${eventId}`,
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log("Response data:", data);

            if (data.id) {
                alert("Miembro del personal añadido al evento con éxito.");
            } else {
                alert("Error al añadir miembro del personal al evento.");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}
