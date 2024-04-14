let ws = false;

function toggleLike(index) {
    if (posts[index].liked) {
        posts[index].likes--;
    } else {
        posts[index].likes++;
    }
    posts[index].liked = !posts[index].liked;
    renderPosts();
}

//document.getElementById('createPostBtn').addEventListener('click', function() {
//    document.getElementById('popup').style.display = 'block';
//});
//
//document.getElementById('cancelPostBtn').addEventListener('click', function() {
//    document.getElementById('popup').style.display = 'none';
//});
//
//document.getElementById('submitPostBtn').addEventListener('click', function() {
//    const content = document.getElementById('postContent').value.trim();
//    if (content !== '') {
//        const post = {
//            username: 'User', // You can replace 'User' with actual username
//            content: content,
//            likes: 0,
//            liked: false
//        };
//        posts.push(post);
//        renderPosts();
//        document.getElementById('popup').style.display = 'none';
//        document.getElementById('postContent').value = '';
//    }
//});

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
//        const xsrfToken = document.getElementById("xsrf_token").value;
//        request.setRequestHeader("X-XSRF-Token", xsrfToken);
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

function Welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    updateChat();

    if (ws) {
        initWS();
    } else {
//        const videoElem = document.getElementsByClassName('video-chat')[0];
//        videoElem.parentElement.removeChild(videoElem);
        setInterval(updateChat, 5000);
    }
}

