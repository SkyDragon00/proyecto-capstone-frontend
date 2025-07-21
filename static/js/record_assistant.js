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
                Swal.fire({
                    title: "Error de búsqueda",
                    text: "Ocurrió un error al buscar el asistente. Revise si la identificación es correcta.",
                    icon: "error",
                    confirmButtonText: "Entendido",
                });
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
                Swal.fire({
                    title: "No registrado",
                    text: "La persona no se encuentra registrada en el evento.",
                    icon: "warning",
                    confirmButtonText: "Entendido",
                });
            } else if (
                typeof data.detail === "string" &&
                data.detail.includes("Duplicate entry")
            ) {
                Swal.fire({
                    title: "Ya registrado",
                    text: "La persona ya se encuentra registrada en el evento.",
                    icon: "info",
                    confirmButtonText: "Entendido",
                });
            } else {
                Swal.fire({
                    title: "Asistencia registrada",
                    text: "Asistencia registrada correctamente.",
                    icon: "success",
                    confirmButtonText: "OK",
                }).then(() => {
                    window.location.href = `/record-assistant/${eventId}/${eventDateId}`;
                });
            }
        })
        .catch((error) => {
            console.log(error);
            Swal.fire({
                title: "Error",
                text: "Error: " + error,
                icon: "error",
                confirmButtonText: "Entendido",
            }).then(() => {
                location.reload();
            });
        });

    // location.reload();
}
