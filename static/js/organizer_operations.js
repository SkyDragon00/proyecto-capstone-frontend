// static/js/organizer_operations.js

/**
 * Elimina un organizador por su ID.
 * @param {number} organizerId
 */
async function deleteOrganizer(organizerId) {
    if (!confirm("¿Estás seguro de que deseas eliminar este organizador?")) {
        return;
    }

    try {
        console.log("Enviando petición DELETE para organizador:", organizerId);
        console.log("Cookies disponibles:", document.cookie);
        
        const response = await fetch(`/delete-organizer/${organizerId}`, {
            method: "DELETE",
            credentials: 'include',  // ¡Envía cookies incluyendo access_token!
            headers: {
                'Accept': 'application/json'  // Para que el backend devuelva JSON
            }
        });

        console.log("Respuesta recibida:", response.status, response.statusText);

        if (response.ok) {
            const result = await response.json();
            alert(result.message || "Organizador eliminado con éxito");
            
            // Remover la fila de la tabla en lugar de recargar toda la página
            const row = document.getElementById(`organizer-row-${organizerId}`);
            if (row) {
                row.remove();
            } else {
                location.reload(); // Fallback si no se encuentra la fila
            }
        } else if (response.status === 401) {
            alert("Sesión expirada. Redirigiendo al login...");
            window.location.href = '/login';
        } else {
            let errorMessage = "Error al eliminar el organizador";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (jsonError) {
                console.warn("No se pudo parsear la respuesta de error como JSON:", jsonError);
            }
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error("Error al eliminar organizador:", error);
        alert("Error: " + error.message);
    }
}

