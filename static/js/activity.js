async function submitActivity() {
    const activity_type = document.getElementById('Activity_Type').value;
    const calories_burned = document.getElementById('Calories_Burned').value;
    const duration = document.getElementById('Duration').value;
    const messageDiv = document.getElementById('message');

    if (!activity_type || !calories_burned || !duration) {
        messageDiv.textContent = 'Please fill in all fields.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    if (calories_burned <= 0 || duration <= 0) {
        messageDiv.textContent = 'Calories and duration must be positive.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = {
        activity_type,
        calories_burned: parseInt(calories_burned),
        duration: parseInt(duration)
    };

    try {
        const response = await fetch('/activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = 'Activity logged successfully!';
            messageDiv.classList.remove('error');
        } else {
            messageDiv.textContent = result.error || 'Failed to log activity.';
            messageDiv.classList.add('error');
        }
        messageDiv.style.display = 'block';
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}