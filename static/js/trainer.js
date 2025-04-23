async function submitTrainer() {
    const trainer_id = document.getElementById('trainer_id').value;
    const name = document.getElementById('name').value;
    const specialization = document.getElementById('specialization').value;
    const messageDiv = document.getElementById('message');

    if (!trainer_id || !name || !specialization) {
        messageDiv.textContent = 'Please fill in all fields.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { trainer_id, name, specialization };

    try {
        const response = await fetch('/trainer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Trainer added successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to add trainer.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}