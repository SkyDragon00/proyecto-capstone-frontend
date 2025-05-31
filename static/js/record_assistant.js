function sendAttendance(eventDateId, eventId, assistantId) {
    //    curl -X 'POST' \
    //   'http://127.0.0.1:8000/events/add/attendance/1/5/3' \
    //   -H 'accept: application/json' \
    //   -d ''
    fetch(
        `http://127.0.0.1:8000/events/add/attendance/${eventDateId}/${eventId}/${assistantId}`,
        {
            method: "POST",
            headers: {
                accept: "application/json",
            },
        }
    )
        .then((response) => response.json())
        .then((data) => alert(JSON.stringify(data)))
        .catch((error) => alert("Error: " + error));

    // Ahora recarga la página
    location.reload();
}
