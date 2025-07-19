async function addCompanion(eventId) {
    const companionIdentification = document.getElementById(
        "companion_identification"
    ).value;

    // curl -X 'GET' \
    //   'http://127.0.0.1:8000/assistant/get-by-id-number/1750319731' \
    //   -H 'accept: application/json'
    if (!companionIdentification) {
        alert("Por favor, ingresa la identificación del acompañante.");
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
            alert(
                `Acompañante encontrado: ${data.first_name} ${data.last_name}.`
            );
        })
        .catch((error) => {
            console.error(error);
            alert(
                "Ocurrió un error al añadir el acompañante. Revise si la identificación es correcta."
            );
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
            alert("Acompañante añadido al evento con éxito.");
        })
        .catch((error) => {
            console.error(error);
            alert("Ocurrió un error al añadir el acompañante al evento.");
        });
}
