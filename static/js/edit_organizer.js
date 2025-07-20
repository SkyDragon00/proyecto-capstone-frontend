// static/js/edit_organizer.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("edit-form");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const firstName = formData.get("first_name");
        const lastName = formData.get("last_name");
        const email = formData.get("email");
        const password = formData.get("password");

        // Validar que al menos un campo esté lleno
        if (!firstName && !lastName && !email && !password) {
            Swal.fire({
                title: "Campos vacíos",
                text: "Debe proporcionar al menos un campo para actualizar",
                icon: "warning",
                confirmButtonText: "Entendido",
            });
            return;
        }

        // Validar email si se proporciona
        if (email && !isValidEmail(email)) {
            Swal.fire({
                title: "Email inválido",
                text: "Por favor ingrese un email válido",
                icon: "error",
                confirmButtonText: "Entendido",
            });
            return;
        }

        // Validar contraseña si se proporciona
        if (password && !isValidPassword(password)) {
            Swal.fire({
                title: "Contraseña inválida",
                text: "La contraseña debe tener al menos 9 caracteres, 1 letra minúscula, 1 letra mayúscula, 1 dígito y 1 carácter especial",
                icon: "error",
                confirmButtonText: "Entendido",
            });
            return;
        }

        // Enviar el formulario normalmente
        form.submit();
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isValidPassword(password) {
        // Al menos 9 caracteres, 1 minúscula, 1 mayúscula, 1 dígito, 1 carácter especial
        if (password.length < 9) return false;
        if (!/[a-z]/.test(password)) return false;
        if (!/[A-Z]/.test(password)) return false;
        if (!/\d/.test(password)) return false;
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return false;
        return true;
    }
});
