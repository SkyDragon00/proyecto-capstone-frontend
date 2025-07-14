document
    .getElementById("register-button")
    .addEventListener("click", function () {
        const companionsInput = document.getElementById("companions").value;

        const companions = companionsInput
            .split(";")
            .map((c) => c.trim())
            .filter((c) => c);

        console.log("Companions to register:", companions);
    });
