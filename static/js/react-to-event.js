function likeEvent(userId, eventId) {
    fetch(
        `https://proyecto-capstone-backend.onrender.com/assistant/react/${userId}/${eventId}?reaction=like`,
        {
            method: "GET",
        }
    );
    location.reload();
}

function dislikeEvent(userId, eventId) {
    fetch(
        `https://proyecto-capstone-backend.onrender.com/assistant/react/${userId}/${eventId}?reaction=dislike`,
        {
            method: "GET",
        }
    );
    location.reload();
}
