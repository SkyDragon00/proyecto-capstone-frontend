function saveSettings() {
    const model = document.getElementById("model").value;
    const threshold = document.getElementById("threshold").value;

    alert(`Guardando configuración: modelo=${model}, umbral=${threshold}`);

    fetch(
        "http://127.0.0.1:8000/organizer/change-settings?model_name=" +
            model +
            "&threshold=" +
            threshold,
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
