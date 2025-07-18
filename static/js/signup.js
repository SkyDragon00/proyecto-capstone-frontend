function validarCedulaEcuatoriana(cedula) {
    // 1. Requisitos iniciales: 10 dígitos y que sea solo números.
    if (
        typeof cedula !== "string" ||
        cedula.length !== 10 ||
        !/^\d+$/.test(cedula)
    ) {
        return false;
    }

    const provincia = parseInt(cedula.substring(0, 2), 10);
    const tercerDigito = parseInt(cedula[2], 10);

    // 2. El código de la provincia no puede ser mayor a 24 ni menor a 1.
    if (provincia < 1 || provincia > 24) {
        return false;
    }

    // 3. El tercer dígito debe ser menor a 6.
    if (tercerDigito >= 6) {
        return false;
    }

    const digitos = cedula.split("").map(Number);
    const digitoVerificador = digitos.pop(); // Último dígito

    // 4. Algoritmo de validación (Módulo 10).
    const suma = digitos.reduce((acc, current, index) => {
        // Coeficientes: 2, 1, 2, 1, 2, 1, 2, 1, 2
        let valor = current * (index % 2 === 0 ? 2 : 1);

        // Si el resultado es mayor o igual a 10, se le resta 9.
        if (valor >= 10) {
            valor -= 9;
        }
        return acc + valor;
    }, 0);

    // 5. Verificación final.
    const resultado = 10 - (suma % 10);
    const digitoCalculado = resultado === 10 ? 0 : resultado;

    return digitoCalculado === digitoVerificador;
}

document.getElementById("login-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const event = e;
    const firstName = document.getElementById("first_name").value.trim();
    const lastName = document.getElementById("last_name").value.trim();
    const idNumber = document.getElementById("id_number").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document
        .getElementById("confirm_password")
        .value.trim();

    if (
        !firstName ||
        !lastName ||
        !idNumber ||
        !phone ||
        !email ||
        !password ||
        !confirmPassword
    ) {
        event.preventDefault();
        alert("Por favor, complete todos los campos.");
        return;
    }

    // Confirmar que las dos contraseñas coinciden
    if (password !== confirmPassword) {
        event.preventDefault();
        alert("Las contraseñas no coinciden.");
        return;
    }

    // Ver que la contraseña al menos tenga 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial
    const passwordPattern =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8}/;
    if (!passwordPattern.test(password)) {
        event.preventDefault();
        alert(
            "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial."
        );
        return;
    }

    const namePattern = /^[A-Z][a-z]+$/;
    if (!namePattern.test(firstName) || !namePattern.test(lastName)) {
        event.preventDefault();
        alert("El nombre y apellido deben comenzar con mayúscula.");
        return;
    }

    const dateOfBirth = document.getElementById("date_of_birth").value;
    if (dateOfBirth) {
        const today = new Date();
        const birthDate = new Date(dateOfBirth);
        if (birthDate >= today) {
            event.preventDefault();
            alert(
                "La fecha de nacimiento debe ser anterior a la fecha actual."
            );
            return;
        }
    }

    // Validar que si el tipo de cédula es "Cédula", el número de cédula sea válido
    const idType = document.getElementById("id_number_type").value;
    if (idType === "cedula" && !validarCedulaEcuatoriana(idNumber)) {
        event.preventDefault();
        alert("El número de cédula ingresado no es válido.");
        return;
    }

    // Si es pasaporte verificar que tenga 9 caracteres y el primero sea la letra A (passport)
    if (idType === "passport" && !/^[A][0-9]{7}$/.test(idNumber)) {
        event.preventDefault();
        alert("El número de pasaporte ingresado no es válido.");
        return;
    }

    // Validar el teléfono sin codigo de país
    if (!/^\d{10}$/.test(phone)) {
        event.preventDefault();
        alert("El número de teléfono debe tener 10 dígitos.");
        return;
    }

    // Haz esta validación                 if self.email.endswith("udla.edu.ec") or not (self.email.endswith("@gmail.com") or self.email.endswith("@hotmail.com") or self.email.endswith("@outlook.com") or self.email.endswith("@protonmail.com") or self.email.endswith("@yahoo.com")):
    if (email.endsWith("@udla.edu.ec")) {
        event.preventDefault();
        alert(
            "El correo electrónico no puede ser de la universidad. Por favor, utiliza un correo personal."
        );
        return;
    }

    // Verificar que el correo sea de proveedores comunes
    if (
        !(
            email.endsWith("@gmail.com") ||
            email.endsWith("@hotmail.com") ||
            email.endsWith("@outlook.com") ||
            email.endsWith("@protonmail.com") ||
            email.endsWith("@yahoo.com")
        )
    ) {
        event.preventDefault();
        alert(
            "El correo electrónico debe ser de un proveedor común (Gmail, Hotmail, Outlook, ProtonMail, Yahoo)."
        );
        return;
    }

    // Desactiva el botón de envío para evitar múltiples envíos
    const submitButton = document.getElementById("submit-button");
    submitButton.disabled = true;

    const form = e.target;
    const formData = new FormData(form);

    // Elimina el campo confirm_password antes de enviar
    formData.delete("confirm_password");

    fetch("http://127.0.0.1:8000/assistant/add", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (response.ok) {
                window.location.href = "/login";
            } else {
                return response.json().then((errorText) => {
                    if (
                        errorText["detail"].includes(
                            "Face could not be detected"
                        )
                    ) {
                        alert(
                            "No se pudo detectar un único rostro en la imagen. Por favor, asegúrate de que la imagen contenga un solo rostro claro y visible."
                        );
                    } else {
                        alert("Error en el registro: " + errorText.detail);
                    }
                });
            }
        })
        .catch((err) => {
            alert("Error de red: " + err.message);
        });
});
