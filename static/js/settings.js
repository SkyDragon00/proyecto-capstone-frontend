function saveSettings() {
    const model = document.getElementById("model").value;
    let threshold = document.getElementById("threshold").value;

    if (threshold === "") {
        threshold = 0; // Valor por defecto si no se especifica
    }

    fetch(
        `https://proyecto-capstone-backend.onrender.com/organizer/change-settings?model_name=${model}&threshold=${threshold}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((response) => {
        if (response.ok) {
            alert("Configuración guardada con éxito.");
            location.reload();
        } else {
            alert("Error al guardar la configuración.");
        }
    });
}
