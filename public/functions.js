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

function chatMessageHTML(messageJSON) {
    console.log(messageJSON)
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    console.log(messageJSON.id)
    let messageHTML = "<br><button onclick='deleteMessage(\"" + messageId + "\")'>X</button> ";
    messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws) {
        // Using WebSockets
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
    } else {
        // Using AJAX
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log(this.response);
            }
        }
        const messageJSON = {"message": message};
        request.open("POST", "/chat-messages");
        const xsrfToken = document.getElementById("xsrf_token").value;
        request.setRequestHeader("X-XSRF-Token", xsrfToken);
        request.send(JSON.stringify(messageJSON));
    }
    chatTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response)
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-messages");
    request.send();
}