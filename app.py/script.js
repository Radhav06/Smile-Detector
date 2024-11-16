document.addEventListener("DOMContentLoaded", () => {
    const voiceButton = document.getElementById("voice-btn");
    const statusText = document.getElementById("status");

    // Send voice command trigger to the backend
    voiceButton.addEventListener("click", () => {
        fetch('/voice-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            statusText.textContent = `Status: ${data.status}`;
        })
        .catch(error => {
            console.error("Error:", error);
            statusText.textContent = "Status: Error communicating with server.";
        });
    });
});
