function saveSettings() {
    const model = document.getElementById("model").value;
    let threshold = document.getElementById("threshold").value;
    const button = document.querySelector('.a-button-filled-red');
    const originalText = button.textContent;

    // Validación del threshold
    if (threshold === "") {
        threshold = 0.5; // Valor por defecto si no se especifica
    }
    
    const thresholdValue = parseFloat(threshold);
    if (isNaN(thresholdValue) || thresholdValue < 0 || thresholdValue > 1) {
        showMessage("El umbral de confianza debe ser un número entre 0 y 1.", "error");
        return;
    }

    // Estado de carga
    button.disabled = true;
    button.classList.add('loading');
    button.textContent = 'Guardando...';

    // Remover mensajes anteriores
    removeMessages();

    fetch(
        `https://proyecto-capstone-backend.onrender.com/organizer/change-settings?model_name=${model}&threshold=${threshold}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
        }
    )
    .then((response) => {
        if (response.ok) {
            showMessage("Configuración guardada con éxito.", "success");
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        showMessage("Error al guardar la configuración. Por favor, inténtalo de nuevo.", "error");
    })
    .finally(() => {
        // Restaurar estado del botón
        button.disabled = false;
        button.classList.remove('loading');
        button.textContent = originalText;
    });
}

function showMessage(text, type) {
    // Remover mensajes anteriores
    removeMessages();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    
    const form = document.querySelector('.settings-container form');
    form.insertBefore(messageDiv, form.firstChild);
    
    // Auto-remover después de 5 segundos si es mensaje de error
    if (type === 'error') {
        setTimeout(() => {
            removeMessages();
        }, 5000);
    }
}

function removeMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => message.remove());
}

// Validación en tiempo real del threshold
document.addEventListener('DOMContentLoaded', function() {
    const thresholdInput = document.getElementById('threshold');
    
    thresholdInput.addEventListener('input', function() {
        const value = parseFloat(this.value);
        if (isNaN(value) || value < 0 || value > 1) {
            this.style.borderColor = '#dc3545';
        } else {
            this.style.borderColor = '#e0e0e0';
        }
    });
    
    // Formatear el valor cuando se pierde el foco
    thresholdInput.addEventListener('blur', function() {
        const value = parseFloat(this.value);
        if (!isNaN(value) && value >= 0 && value <= 1) {
            this.value = value.toFixed(2);
        }
    });
});
