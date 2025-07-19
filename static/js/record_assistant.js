async function sendAttendance(eventDateId, eventId, assistantId) {
    //    curl -X 'POST' \
    //   'http://127.0.0.1:8000/events/add/attendance/1/5/3' \
    //   -H 'accept: application/json' \
    //   -d ''
    if (!assistantId) {
        const assistantIdentification =
            document.getElementById("assistant_id").value;

        await fetch(
            `${API_URL}/assistant/get-by-id-number/${assistantIdentification}`
        )
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Error en la solicitud");
                }
                return response.json();
            })
            .then((data) => {
                assistantId = data.id;
            })
            .catch((error) => {
                console.error(error);
                alert(
                    "Ocurrió un error al buscar el asistente. Revise si la identificación es correcta."
                );
                throw new Error(
                    "Error al buscar el asistente: " + error.message
                );
            });
    }

    await fetch(
        `${API_URL}/events/add/attendance/${eventDateId}/${eventId}/${assistantId}`,
        {
            method: "POST",
            headers: {
                accept: "application/json",
            },
        }
    )
        .then((response) => response.json())
        .then((data) => {
            if (data.detail == "Registration not found") {
                alert("La persona no se encuentra registrada en el evento.");
            } else if (data.detail.includes("Duplicate entry")) {
                alert("La persona ya se encuentra registrada en el evento.");
            } else {
                alert("Asistencia registrada correctamente.");
            }
        })
        .catch((error) => alert("Error: " + error));

    location.reload();
}
