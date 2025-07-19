function likeEvent(userId, eventId) {
    fetch(`${API_URL}/assistant/react/${userId}/${eventId}?reaction=like`, {
        method: "GET",
    });
    location.reload();
}

function dislikeEvent(userId, eventId) {
    fetch(`${API_URL}/assistant/react/${userId}/${eventId}?reaction=dislike`, {
        method: "GET",
    });
    location.reload();
}
