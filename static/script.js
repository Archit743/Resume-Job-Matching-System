document.getElementById('signupForm').onsubmit = function(event) {
    event.preventDefault();
    
    // Disable the submit button to prevent double submission
    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    
    const userData = {
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        password: document.getElementById('password').value.trim()
    };

    fetch('/auth/signup', {  // Updated URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
        credentials: 'same-origin'  // Important for session handling
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            document.getElementById('signupForm').reset();
            // Optionally switch to login form or redirect
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    })
    .finally(() => {
        submitButton.disabled = false;  // Re-enable the submit button
    });
};

document.getElementById('loginForm').onsubmit = function(event) {
    event.preventDefault();
    
    // Disable the submit button to prevent double submission
    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    
    const loginData = {
        email_or_phone: document.getElementById('email_or_phone').value.trim(),
        password: document.getElementById('login_password').value.trim()
    };

    fetch('/auth/login', {  // Updated URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
        credentials: 'same-origin'  // Important for session handling
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    })
    .finally(() => {
        submitButton.disabled = false;  // Re-enable the submit button
    });
};