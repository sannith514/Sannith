document.getElementById('loginForm').addEventListener('submit', function(event) {
    
    const email = document.getElementById('email').value;
    if(!email.includes('@')) {
        alert("Please enter a valid email address.");
        event.preventDefault(); 
    }

    
});
