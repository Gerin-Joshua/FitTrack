async function submitBadge() {
    const badge_type = document.getElementById('badge_type').value;
    const badge_desc = document.getElementById('badge_desc').value;
    const messageDiv = document.getElementById('message');

    if (!badge_type || !badge_desc) {
        messageDiv.textContent = 'Please fill in all fields.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { badge_type, badge_desc };

    try {
        const response = await fetch('/badge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Badge added successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to add badge.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}