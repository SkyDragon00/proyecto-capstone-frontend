function addStaffToEvent() {
    const staffId = document.getElementById("staff-id").value;
    const eventId = document.getElementById("event-id").value;

    if (!staffId) {
        Swal.fire({
            title: "Selección requerida",
            text: "Por favor, selecciona un miembro del personal.",
            icon: "warning",
            confirmButtonText: "Entendido",
        });
        return;
    }

    fetch(`${API_URL}/staff/add-staff-to-event`, {
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
                Swal.fire({
                    title: "Staff añadido",
                    text: "Miembro del personal añadido al evento con éxito.",
                    icon: "success",
                    confirmButtonText: "OK",
                });
            } else {
                Swal.fire({
                    title: "Error",
                    text: "Error al añadir miembro del personal al evento.",
                    icon: "error",
                    confirmButtonText: "Intentar de nuevo",
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}
