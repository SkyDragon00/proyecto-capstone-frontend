function saveSettings() {
    const model = document.getElementById("model").value;
    let threshold = document.getElementById("threshold").value;

    if (threshold === "") {
        threshold = 0; // Valor por defecto si no se especifica
    }

    fetch(
        `${API_URL}/organizer/change-settings?model_name=${model}&threshold=${threshold}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((response) => {
        if (response.ok) {
            Swal.fire({
                title: "Configuración guardada",
                text: "Configuración guardada con éxito.",
                icon: "success",
                confirmButtonText: "OK",
            }).then(() => {
                location.reload();
            });
        } else {
            Swal.fire({
                title: "Error",
                text: "Error al guardar la configuración.",
                icon: "error",
                confirmButtonText: "Intentar de nuevo",
            });
        }
    });
}
