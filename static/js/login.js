async function login() {
    const user_id = document.getElementById('user_id').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');

    if (!user_id || !password) {
        messageDiv.textContent = 'Please fill in all fields.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
        return;
    }

    const data = { user_id, password };

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            messageDiv.textContent = result.error || 'Login failed.';
            messageDiv.classList.add('error');
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
        messageDiv.classList.add('error');
        messageDiv.style.display = 'block';
    }
}