async function addCompanion(eventId) {
    const companionIdentification = document.getElementById(
        "companion_identification"
    ).value;

    // curl -X 'GET' \
    //   'http://127.0.0.1:8000/assistant/get-by-id-number/1750319731' \
    //   -H 'accept: application/json'
    if (!companionIdentification) {
        Swal.fire({
            title: "Identificación requerida",
            text: "Por favor, ingresa la identificación del acompañante.",
            icon: "warning",
            confirmButtonText: "Entendido",
        });
        return;
    }

    let acompañante;

    await fetch(
        `${API_URL}/assistant/get-by-id-number/${companionIdentification}`
    )
        .then((response) => {
            if (!response.ok) {
                throw new Error("Error en la solicitud");
            }
            return response.json();
        })
        .then((data) => {
            acompañante = data;
            Swal.fire({
                title: "Acompañante encontrado",
                text: `Acompañante encontrado: ${data.first_name} ${data.last_name}.`,
                icon: "success",
                confirmButtonText: "Continuar",
            });
        })
        .catch((error) => {
            console.error(error);
            Swal.fire({
                title: "Error de búsqueda",
                text: "Ocurrió un error al añadir el acompañante. Revise si la identificación es correcta.",
                icon: "error",
                confirmButtonText: "Entendido",
            });
            return;
        });

    // Obtener la cookie de sesión access_token
    const accessToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];

    fetch(`${API_URL}/assistant/register-companion-to-event/${eventId}`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `companion_id=${acompañante.id}&companion_type=first_grade`,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Error en la solicitud");
            }
            return response.json();
        })
        .then((data) => {
            Swal.fire({
                title: "Acompañante añadido",
                text: "Acompañante añadido al evento con éxito.",
                icon: "success",
                confirmButtonText: "OK",
            });
        })
        .catch((error) => {
            console.error(error);
            Swal.fire({
                title: "Error",
                text: "Ocurrió un error al añadir el acompañante al evento.",
                icon: "error",
                confirmButtonText: "Intentar de nuevo",
            });
        });
}
