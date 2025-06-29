document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const registerMessage = document.getElementById('registerMessage');
    const loginMessage = document.getElementById('loginMessage');
    const logoutButton = document.getElementById('logoutButton');

    const API_BASE_URL = '/api'; // Assuming API is served from the same origin

    // Check initial login state
    if (localStorage.getItem('accessToken')) {
        loginMessage.textContent = 'Already logged in. Token: ' + localStorage.getItem('accessToken').substring(0, 20) + '...';
        loginMessage.className = 'message success';
        loginMessage.style.display = 'block';
        logoutButton.style.display = 'block';
    }

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            });
            const data = await response.json();
            if (response.ok) {
                registerMessage.textContent = `User ${data.username} registered successfully!`;
                registerMessage.className = 'message success';
            } else {
                registerMessage.textContent = `Error: ${data.detail || response.statusText}`;
                registerMessage.className = 'message error';
            }
        } catch (error) {
            registerMessage.textContent = `Network Error: ${error.message}`;
            registerMessage.className = 'message error';
        }
        registerMessage.style.display = 'block';
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        // FastAPI's OAuth2PasswordRequestForm expects form data, not JSON
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        // formData.append('scope', ''); // Optional: if you use scopes
        // formData.append('client_id', ''); // Optional
        // formData.append('client_secret', ''); // Optional

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
                body: formData,
            });
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('accessToken', data.access_token);
                loginMessage.textContent = 'Login successful! Token stored.';
                loginMessage.className = 'message success';
                logoutButton.style.display = 'block';
            } else {
                loginMessage.textContent = `Error: ${data.detail || response.statusText}`;
                loginMessage.className = 'message error';
            }
        } catch (error) {
            loginMessage.textContent = `Network Error: ${error.message}`;
            loginMessage.className = 'message error';
        }
        loginMessage.style.display = 'block';
    });

    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('accessToken');
        loginMessage.textContent = 'Logged out successfully.';
        loginMessage.className = 'message success';
        loginMessage.style.display = 'block';
        logoutButton.style.display = 'none';
        // Optionally redirect or clear other user-specific data
    });
});
