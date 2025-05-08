async function submitFriend() {
    const friend_id = document.getElementById('friend_id').value;
    const friendship_streak = document.getElementById('friendship_streak').value;
    const messageDiv = document.getElementById('message');

    if (!friend_id || !friendship_streak || friendship_streak < 0) {
        messageDiv.textContent = 'Please fill in all fields correctly.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { friend_id, friendship_streak: parseInt(friendship_streak) };

    try {
        const response = await fetch('/friend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Friend added successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to add friend.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}