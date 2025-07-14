async function sendAttendance(eventDateId, eventId, assistantId) {
    //    curl -X 'POST' \
    //   'http://127.0.0.1:8000/events/add/attendance/1/5/3' \
    //   -H 'accept: application/json' \
    //   -d ''
    if (!assistantId) {
        const assistantIdentification =
            document.getElementById("assistant_id").value;

        await fetch(
            `http://127.0.0.1:8000/assistant/get-by-id-number/${assistantIdentification}`
        )
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Error en la solicitud");
                }
                return response.json();
            })
            .then((data) => {
                assistantId = data.id;
                alert(
                    `Acompañante encontrado: ${data.first_name} ${data.last_name}.`
                );
            })
            .catch((error) => {
                console.error(error);
                alert(
                    "Ocurrió un error al buscar el asistente. Revise si la identificación es correcta."
                );
                return;
            });
    }

    await fetch(
        `http://127.0.0.1:8000/events/add/attendance/${eventDateId}/${eventId}/${assistantId}`,
        {
            method: "POST",
            headers: {
                accept: "application/json",
            },
        }
    )
        .then((response) => response.json())
        .then((data) => alert("Asistencia registrada correctamente."))
        .catch((error) => alert("Error: " + error));

    // Ahora recarga la página
    location.reload();
}
