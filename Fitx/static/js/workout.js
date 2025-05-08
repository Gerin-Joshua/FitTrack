async function submitWorkout() {
    const plan_type = document.getElementById('plan_type').value;
    const duration = document.getElementById('duration').value;
    const messageDiv = document.getElementById('message');

    if (!plan_type || !duration || duration <= 0) {
        messageDiv.textContent = 'Please fill in all fields correctly.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { plan_type, duration: parseInt(duration) };

    try {
        const response = await fetch('/workout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Workout plan created successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to create plan.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}