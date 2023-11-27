document.getElementById('registerForm').addEventListener('submit', function(event) {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if(password !== confirmPassword) {
        alert("Passwords do not match.");
        event.preventDefault(); 
    }

    
});
