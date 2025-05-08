async function submitDiet() {
    const calories = document.getElementById('calories').value;
    const messageDiv = document.getElementById('message');

    if (!calories || calories <= 0) {
        messageDiv.textContent = 'Please enter a valid calorie amount.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { calories: parseInt(calories) };

    try {
        const response = await fetch('/diet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Diet logged successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to log diet.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}