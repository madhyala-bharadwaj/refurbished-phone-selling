// static/login.js

document.addEventListener('DOMContentLoaded', () => {
    const apiBaseUrl = 'http://localhost:8000';
    const loginBtn = document.getElementById('login-btn');
    const authStatus = document.getElementById('auth-status');

    loginBtn.addEventListener('click', async () => {
        authStatus.textContent = 'Logging in...';
        try {
            const response = await fetch(`${apiBaseUrl}/token?username=admin&password=password`, { 
                method: 'POST' 
            });

            if (!response.ok) {
                throw new Error('Login failed. Please check credentials.');
            }

            const data = await response.json();
            
            // Store the token in sessionStorage, which persists across page loads
            sessionStorage.setItem('authToken', data.access_token);

            // Redirect to the main application page
            window.location.href = '/app';

        } catch (error) {
            authStatus.textContent = error.message;
        }
    });
});
