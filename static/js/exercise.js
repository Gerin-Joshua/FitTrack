async function submitExercise() {
    const plan_id = document.getElementById('plan_id').value;
    const exercise_type = document.getElementById('exercise_type').value;
    const messageDiv = document.getElementById('message');

    if (!plan_id || !exercise_type || plan_id <= 0) {
        messageDiv.textContent = 'Please fill in all fields correctly.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { plan_id: parseInt(plan_id), exercise_type };

    try {
        const response = await fetch('/exercise', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Exercise added successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to add exercise.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}