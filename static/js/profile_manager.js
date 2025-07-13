/**
 * Profile Management JavaScript
 * Handles profile update and delete operations with enhanced UX
 */

class ProfileManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormValidation();
    }

    bindEvents() {
        // Bind edit form toggle
        const editButton = document.querySelector('[onclick="toggleEditForm()"]');
        if (editButton) {
            editButton.removeAttribute('onclick');
            editButton.addEventListener('click', this.toggleEditForm.bind(this));
        }

        // Bind delete button
        const deleteButton = document.querySelector('[onclick="confirmDeleteProfile()"]');
        if (deleteButton) {
            deleteButton.removeAttribute('onclick');
            deleteButton.addEventListener('click', this.confirmDeleteProfile.bind(this));
        }

        // Bind form submission
        const profileForm = document.getElementById('profileEditForm');
        if (profileForm) {
            profileForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        }

        // Bind overlay click to close
        const editForm = document.getElementById('editForm');
        if (editForm) {
            editForm.addEventListener('click', this.handleOverlayClick.bind(this));
        }

        // Bind close button
        const closeButton = document.querySelector('.close-btn');
        if (closeButton) {
            closeButton.addEventListener('click', this.toggleEditForm.bind(this));
        }

        // Bind cancel button
        const cancelButton = document.querySelector('.btn-secondary');
        if (cancelButton) {
            cancelButton.addEventListener('click', this.toggleEditForm.bind(this));
        }
    }

    setupFormValidation() {
        const form = document.getElementById('profileEditForm');
        if (!form) return;

        // Add real-time validation
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateField.bind(this));
            input.addEventListener('input', this.clearFieldError.bind(this));
        });
    }

    validateField(event) {
        const field = event.target;
        const value = field.value.trim();
        
        // Clear previous error
        this.clearFieldError(event);

        // Validate based on field type
        let isValid = true;
        let errorMessage = '';

        switch (field.type) {
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    isValid = false;
                    errorMessage = 'Por favor ingrese un email válido';
                }
                break;
            case 'tel':
                if (value && !this.isValidPhone(value)) {
                    isValid = false;
                    errorMessage = 'Por favor ingrese un teléfono válido';
                }
                break;
            case 'password':
                if (value && value.length < 6) {
                    isValid = false;
                    errorMessage = 'La contraseña debe tener al menos 6 caracteres';
                }
                break;
            case 'text':
                if (field.name === 'id_number' && value && !this.isValidIdNumber(value)) {
                    isValid = false;
                    errorMessage = 'Por favor ingrese una cédula válida (10 dígitos) o pasaporte válido (ej: A1234567)';
                }
                break;
        }

        if (!isValid) {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    clearFieldError(event) {
        const field = event.target;
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
        field.classList.remove('error');
    }

    showFieldError(field, message) {
        // Remove existing error
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // Add error styling
        field.classList.add('error');

        // Add error message
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        errorElement.style.color = '#dc3545';
        errorElement.style.fontSize = '12px';
        errorElement.style.marginTop = '4px';
        
        field.parentNode.appendChild(errorElement);
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        // Basic phone validation - adjust regex as needed
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 7;
    }

    isValidIdNumber(idNumber) {
        // Cédula ecuatoriana: exactamente 10 dígitos
        const cedulaPattern      = /^\d{10}$/;
        // Pasaporte: 1–3 letras seguidas de 4–8 dígitos (más flexible)
        const passportAlphaNum   = /^[A-Za-z]{1,3}\d{4,8}$/;
        // Pasaporte numérico: 6–9 dígitos
        const passportNumeric    = /^\d{6,9}$/;

        return cedulaPattern.test(idNumber)
            || passportAlphaNum.test(idNumber)
            || passportNumeric.test(idNumber);
    }

    toggleEditForm() {
        const editForm = document.getElementById('editForm');
        if (!editForm) return;

        if (editForm.style.display === 'none' || editForm.style.display === '') {
            editForm.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
            this.focusFirstInput();
        } else {
            editForm.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restore scrolling
        }
    }

    focusFirstInput() {
        const firstInput = document.querySelector('#editForm input:not([type="hidden"])');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    handleOverlayClick(event) {
        if (event.target === event.currentTarget) {
            this.toggleEditForm();
        }
    }

    confirmDeleteProfile() {
        // Create custom confirmation modal for better UX
        const confirmed = this.showDeleteConfirmationModal();
        if (confirmed) {
            this.deleteProfile();
        }
    }

    showDeleteConfirmationModal() {
        const modal = document.createElement('div');
        modal.className = 'delete-confirmation-modal';
        modal.innerHTML = `
            <div class="modal-overlay">
                <div class="modal-content">
                    <h3>¿Confirmar eliminación?</h3>
                    <p>¿Estás seguro de que deseas eliminar tu perfil? Esta acción no se puede deshacer.</p>
                    <div class="modal-actions">
                        <button class="btn btn-secondary cancel-delete">Cancelar</button>
                        <button class="btn btn-danger confirm-delete">Eliminar</button>
                    </div>
                </div>
            </div>
        `;

        // Add modal styles
        const style = document.createElement('style');
        style.textContent = `
            .delete-confirmation-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 2000;
            }
            .modal-overlay {
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.6);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-content {
                background: white;
                border-radius: 10px;
                padding: 30px;
                max-width: 400px;
                width: 90%;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
            .modal-content h3 {
                margin: 0 0 15px 0;
                color: #dc3545;
            }
            .modal-content p {
                margin: 0 0 25px 0;
                color: #666;
                line-height: 1.5;
            }
            .modal-actions {
                display: flex;
                gap: 15px;
                justify-content: center;
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(modal);

        return new Promise((resolve) => {
            modal.querySelector('.cancel-delete').addEventListener('click', () => {
                document.body.removeChild(modal);
                document.head.removeChild(style);
                resolve(false);
            });

            modal.querySelector('.confirm-delete').addEventListener('click', () => {
                document.body.removeChild(modal);
                document.head.removeChild(style);
                resolve(true);
            });

            // Close on overlay click
            modal.querySelector('.modal-overlay').addEventListener('click', (e) => {
                if (e.target === e.currentTarget) {
                    document.body.removeChild(modal);
                    document.head.removeChild(style);
                    resolve(false);
                }
            });
        });
    }

    async deleteProfile() {
        try {
            this.showLoadingState('Eliminando perfil...');
            
            const response = await fetch('/profile', {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            this.hideLoadingState();

            if (response.ok) {
                const result = await response.json();
                this.showSuccessMessage(result.message || 'Perfil eliminado con éxito');
                
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = '/logout';
                }, 1500);
            } else {
                const error = await response.json();
                this.showErrorMessage('Error al eliminar el perfil: ' + (error.detail || 'Error desconocido'));
            }
        } catch (error) {
            this.hideLoadingState();
            console.error('Error:', error);
            this.showErrorMessage('Error al eliminar el perfil. Por favor, inténtalo de nuevo.');
        }
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        
        // Validate all fields
        const inputs = form.querySelectorAll('input, select');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField({ target: input })) {
                isValid = false;
            }
        });

        if (!isValid) {
            this.showErrorMessage('Por favor corrija los errores antes de continuar');
            return;
        }

        // Remove empty fields to avoid overwriting with empty values
        const fieldsToCheck = ['first_name', 'last_name', 'email', 'password', 'phone', 'id_number', 'gender', 'date_of_birth'];
        
        for (const field of fieldsToCheck) {
            if (!formData.get(field) || formData.get(field).trim() === '') {
                formData.delete(field);
            }
        }

        try {
            this.showLoadingState('Actualizando perfil...');
            
            const response = await fetch('/profile/update', {
                method: 'POST',
                body: formData
            });

            this.hideLoadingState();

            if (response.ok) {
                this.showSuccessMessage('Perfil actualizado con éxito');
                
                // Reload page after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                const error = await response.text();
                this.showErrorMessage('Error al actualizar el perfil: ' + error);
            }
        } catch (error) {
            this.hideLoadingState();
            console.error('Error:', error);
            this.showErrorMessage('Error al actualizar el perfil. Por favor, inténtalo de nuevo.');
        }
    }

    showLoadingState(message) {
        const loader = document.createElement('div');
        loader.id = 'profile-loader';
        loader.innerHTML = `
            <div class="loader-overlay">
                <div class="loader-content">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            </div>
        `;

        const style = document.createElement('style');
        style.id = 'loader-styles';
        style.textContent = `
            #profile-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 3000;
            }
            .loader-overlay {
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .loader-content {
                background: white;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                min-width: 200px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(loader);
    }

    hideLoadingState() {
        const loader = document.getElementById('profile-loader');
        const styles = document.getElementById('loader-styles');
        
        if (loader) document.body.removeChild(loader);
        if (styles) document.head.removeChild(styles);
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        const messageEl = document.createElement('div');
        messageEl.className = `profile-message ${type}`;
        messageEl.textContent = message;

        const style = document.createElement('style');
        style.textContent = `
            .profile-message {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 5px;
                color: white;
                z-index: 4000;
                max-width: 300px;
                word-wrap: break-word;
                animation: slideIn 0.3s ease-out;
            }
            .profile-message.success {
                background-color: #28a745;
            }
            .profile-message.error {
                background-color: #dc3545;
            }
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(messageEl);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(messageEl)) {
                document.body.removeChild(messageEl);
                document.head.removeChild(style);
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfileManager();
});

// Legacy support for inline onclick handlers (fallback)
function toggleEditForm() {
    const manager = new ProfileManager();
    manager.toggleEditForm();
}

function confirmDeleteProfile() {
    const manager = new ProfileManager();
    manager.confirmDeleteProfile();
}
