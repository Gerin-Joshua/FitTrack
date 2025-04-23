async function submitGoal() {
    const goal_type = document.getElementById('goal_type').value;
    const exer_hours = document.getElementById('exer_hours').value;
    const target_weight = document.getElementById('target_weight').value;
    const messageDiv = document.getElementById('message');

    if (!goal_type || !exer_hours || !target_weight) {
        messageDiv.textContent = 'Please fill in all fields.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { goal_type, exer_hours: parseInt(exer_hours), target_weight: parseFloat(target_weight) };

    try {
        const response = await fetch('/goal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Goal set successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to set goal.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}