// static/js/organizer_operations.js

/**
 * Elimina un organizador por su ID.
 * @param {number} organizerId
 */
async function deleteOrganizer(organizerId) {
    const result = await Swal.fire({
        title: "¿Estás seguro?",
        text: "¿Estás seguro de que deseas eliminar este organizador?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
    });

    if (!result.isConfirmed) {
        return;
    }

    try {
        console.log("Enviando petición DELETE para organizador:", organizerId);
        console.log("Cookies disponibles:", document.cookie);

        const response = await fetch(`/delete-organizer/${organizerId}`, {
            method: "DELETE",
            credentials: "include", // ¡Envía cookies incluyendo access_token!
            headers: {
                Accept: "application/json", // Para que el backend devuelva JSON
            },
        });

        console.log(
            "Respuesta recibida:",
            response.status,
            response.statusText
        );

        if (response.ok) {
            const result = await response.json();
            Swal.fire({
                title: "Organizador eliminado",
                text: result.message || "Organizador eliminado con éxito",
                icon: "success",
                confirmButtonText: "OK",
            });

            // Remover la fila de la tabla en lugar de recargar toda la página
            const row = document.getElementById(`organizer-row-${organizerId}`);
            if (row) {
                row.remove();
            } else {
                location.reload(); // Fallback si no se encuentra la fila
            }
        } else if (response.status === 401) {
            Swal.fire({
                title: "Sesión expirada",
                text: "Sesión expirada. Redirigiendo al login...",
                icon: "warning",
                confirmButtonText: "OK",
            }).then(() => {
                window.location.href = "/login";
            });
        } else {
            let errorMessage = "Error al eliminar el organizador";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (jsonError) {
                console.warn(
                    "No se pudo parsear la respuesta de error como JSON:",
                    jsonError
                );
            }
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error("Error al eliminar organizador:", error);
        Swal.fire({
            title: "Error",
            text: "Error: " + error.message,
            icon: "error",
            confirmButtonText: "Entendido",
        });
    }
}
