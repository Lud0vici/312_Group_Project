function welcome(){
    document.getElementById("intro").innerHTML += "<br>Prepare for trouble! And make it double! 😆";
}

// validate the password on the frontend for a visual pw check
function checkPassword() {
    var password = document.getElementById('password').value;
    var confirm_password = document.getElementById('confirm-password').value;
    var checklistItems = document.querySelectorAll('#password-checklist li');

    // Reset checklist
    checklistItems.forEach(function(item) {
        item.className = 'uncompleted';
    });

    // Check password length
    if (password.length >= 8) {
        document.getElementById('length').className = 'completed';
    }

    // Check for uppercase letter
    if (/[A-Z]/.test(password)) {
        document.getElementById('uppercase').className = 'completed';
    }

    // Check for lowercase letter
    if (/[a-z]/.test(password)) {
        document.getElementById('lowercase').className = 'completed';
    }

    // Check for number
    if (/\d/.test(password)) {
        document.getElementById('number').className = 'completed';
    }

    // Check for special character
    if (/[^A-Za-z0-9]/.test(password)) {
        document.getElementById('special').className = 'completed';
    }

    // Check if passwords match
    if (password === confirm_password && confirm_password !== '') {
        document.getElementById('match').className = 'completed';
    }
}