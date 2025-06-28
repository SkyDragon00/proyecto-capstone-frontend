// Request body

// application/x-www-form-urlencoded
// staff_id *
// integer
// The ID of the staff to be added to the event

// event_id *
// integer
// The ID of the event to which the staff is to be added

// curl -X 'POST' \
//   'http://127.0.0.1:8000/staffadd-staff-to-event' \
//   -H 'accept: application/json' \
//   -H 'Content-Type: application/x-www-form-urlencoded' \
//   -d 'staff_id=3&event_id=5'
alert("Añadir miembro del personal a un evento");
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
