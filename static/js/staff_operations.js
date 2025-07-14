/**
 * Staff Operations JavaScript Module
 * Handles staff management operations like create, update, delete
 */

class StaffOperations {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Initialize form validations
        this.setupFormValidation();
        
        // Initialize delete confirmations
        this.setupDeleteConfirmations();
    }

    setupFormValidation() {
        // Create Staff Form Validation
        const createForm = document.getElementById('login-form');
        if (createForm && createForm.action.includes('/create-staff')) {
            createForm.addEventListener('submit', this.validateCreateStaffForm.bind(this));
        }

        // Edit Staff Form Validation
        const editForm = document.getElementById('edit-staff-form');
        if (editForm) {
            editForm.addEventListener('submit', this.validateEditStaffForm.bind(this));
        }
    }

    setupDeleteConfirmations() {
        // Add event listeners for delete buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-delete')) {
                e.preventDefault();
                const button = e.target.closest('.btn-delete');
                const staffId = button.getAttribute('data-staff-id') || 
                              button.getAttribute('onclick')?.match(/\d+/)?.[0];
                if (staffId) {
                    this.confirmDelete(staffId);
                }
            }
        });
    }

    validateCreateStaffForm(e) {
        const formData = new FormData(e.target);
        const firstName = formData.get('first_name')?.trim();
        const lastName = formData.get('last_name')?.trim();
        const email = formData.get('email')?.trim();
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');

        // Validate required fields
        if (!firstName || !lastName || !email || !password || !confirmPassword) {
            e.preventDefault();
            this.showError('Todos los campos son obligatorios.');
            return false;
        }

        // Validate email format
        if (!this.isValidEmail(email)) {
            e.preventDefault();
            this.showError('Por favor, introduce un email válido.');
            return false;
        }

        // Validate password match
        if (password !== confirmPassword) {
            e.preventDefault();
            this.showError('Las contraseñas no coinciden.');
            return false;
        }

        // Validate password strength
        if (!this.isValidPassword(password)) {
            e.preventDefault();
            this.showError('La contraseña debe tener al menos 8 caracteres.');
            return false;
        }

        return true;
    }

    validateEditStaffForm(e) {
        const formData = new FormData(e.target);
        const firstName = formData.get('first_name')?.trim();
        const lastName = formData.get('last_name')?.trim();
        const email = formData.get('email')?.trim();
        const password = formData.get('password');

        // Check if at least one field is modified
        if (!firstName && !lastName && !email && !password) {
            e.preventDefault();
            this.showError('Debes modificar al menos un campo para actualizar.');
            return false;
        }

        // Validate email format if provided
        if (email && !this.isValidEmail(email)) {
            e.preventDefault();
            this.showError('Por favor, introduce un email válido.');
            return false;
        }

        // Validate password if provided
        if (password && !this.isValidPassword(password)) {
            e.preventDefault();
            this.showError('La contraseña debe tener al menos 8 caracteres.');
            return false;
        }

        return true;
    }

    async confirmDelete(staffId) {
        const result = await this.showConfirmDialog(
            '¿Estás seguro?',
            '¿Estás seguro de que quieres eliminar este miembro del staff? Esta acción no se puede deshacer.',
            'Eliminar',
            'Cancelar'
        );

        if (result) {
            await this.deleteStaff(staffId);
        }
    }

    async deleteStaff(staffId) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/staff/delete/${staffId}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess(result.message || 'Staff eliminado correctamente');
                
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
                
            } else {
                const error = await response.json();
                if (error.redirect) {
                    window.location.href = error.redirect;
                } else {
                    this.showError(error.error || 'Error al eliminar el staff');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Error de conexión. Por favor, inténtalo de nuevo.');
        } finally {
            this.showLoading(false);
        }
    }

    // Utility Methods
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPassword(password) {
        return password && password.length >= 8;
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);

        // Add styles if not already present
        this.addNotificationStyles();
    }

    addNotificationStyles() {
        if (document.getElementById('notification-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                animation: slideIn 0.3s ease-out;
            }
            
            .notification-error {
                background: #fee;
                border-left: 4px solid #dc3545;
                color: #721c24;
            }
            
            .notification-success {
                background: #d4edda;
                border-left: 4px solid #28a745;
                color: #155724;
            }
            
            .notification-info {
                background: #d1ecf1;
                border-left: 4px solid #17a2b8;
                color: #0c5460;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem;
            }
            
            .notification-message {
                flex: 1;
                margin-right: 1rem;
            }
            
            .notification-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                opacity: 0.7;
                padding: 0;
                line-height: 1;
            }
            
            .notification-close:hover {
                opacity: 1;
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
            
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #dc2626;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(styles);
    }

    showLoading(show = true) {
        const existingOverlay = document.getElementById('loading-overlay');
        
        if (show && !existingOverlay) {
            const overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(overlay);
        } else if (!show && existingOverlay) {
            existingOverlay.remove();
        }
    }

    async showConfirmDialog(title, message, confirmText = 'Confirmar', cancelText = 'Cancelar') {
        return new Promise((resolve) => {
            const dialog = document.createElement('div');
            dialog.className = 'confirm-dialog-overlay';
            dialog.innerHTML = `
                <div class="confirm-dialog">
                    <div class="confirm-dialog-header">
                        <h3>${title}</h3>
                    </div>
                    <div class="confirm-dialog-body">
                        <p>${message}</p>
                    </div>
                    <div class="confirm-dialog-footer">
                        <button class="btn-cancel">${cancelText}</button>
                        <button class="btn-confirm">${confirmText}</button>
                    </div>
                </div>
            `;

            // Add styles
            this.addConfirmDialogStyles();

            // Add event listeners
            const cancelBtn = dialog.querySelector('.btn-cancel');
            const confirmBtn = dialog.querySelector('.btn-confirm');
            
            cancelBtn.addEventListener('click', () => {
                dialog.remove();
                resolve(false);
            });
            
            confirmBtn.addEventListener('click', () => {
                dialog.remove();
                resolve(true);
            });

            // Close on overlay click
            dialog.addEventListener('click', (e) => {
                if (e.target === dialog) {
                    dialog.remove();
                    resolve(false);
                }
            });

            document.body.appendChild(dialog);
        });
    }

    addConfirmDialogStyles() {
        if (document.getElementById('confirm-dialog-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'confirm-dialog-styles';
        styles.textContent = `
            .confirm-dialog-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10002;
            }
            
            .confirm-dialog {
                background: white;
                border-radius: 8px;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }
            
            .confirm-dialog-header {
                padding: 1.5rem 1.5rem 0;
            }
            
            .confirm-dialog-header h3 {
                margin: 0;
                color: #333;
            }
            
            .confirm-dialog-body {
                padding: 1rem 1.5rem;
            }
            
            .confirm-dialog-body p {
                margin: 0;
                color: #666;
                line-height: 1.5;
            }
            
            .confirm-dialog-footer {
                padding: 0 1.5rem 1.5rem;
                display: flex;
                gap: 1rem;
                justify-content: flex-end;
            }
            
            .btn-cancel,
            .btn-confirm {
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 500;
                transition: background-color 0.2s;
            }
            
            .btn-cancel {
                background: #6c757d;
                color: white;
            }
            
            .btn-cancel:hover {
                background: #5a6268;
            }
            
            .btn-confirm {
                background: #dc3545;
                color: white;
            }
            
            .btn-confirm:hover {
                background: #c82333;
            }
        `;
        document.head.appendChild(styles);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StaffOperations();
});

// Global function for backward compatibility
window.deleteStaff = async function(staffId) {
    const staffOps = new StaffOperations();
    await staffOps.confirmDelete(staffId);
};
