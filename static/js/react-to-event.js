function likeEvent(userId, eventId) {
    fetch(
        `http://127.0.0.1:8000/assistant/react/${userId}/${eventId}?reaction=like`,
        {
            method: "GET",
        }
    );
    location.reload();
}

function dislikeEvent(userId, eventId) {
    fetch(
        `http://127.0.0.1:8000/assistant/react/${userId}/${eventId}?reaction=dislike`,
        {
            method: "GET",
        }
    );
    location.reload();
}
