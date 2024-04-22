const ws = true;
let socket = null;

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('ws://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        console.log(ws_message.data)
        const message = JSON.parse(ws_message.data);
        console.log(message)
        const messageType = message.messageType
        console.log(messageType)
        addMessageToChat(message)
    }
}














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

//function chatMessageHTML(messageJSON) {
//    const messageType = messageJSON.messageType;
//    const username = messageJSON.username;
//    const message = messageJSON.message;
//    const messageId = messageJSON.id;
//
//    if (messageType === 'image') {
//        // If the message is an image, construct HTML to display the image
//        const imgSrc = message; // Assuming 'message' contains the image URL
//        return `<br><button onclick='deleteMessage("${messageId}")'>X</button> <img src="${imgSrc}" class="message-image">`;
//    } else {
//        // If the message is text, construct HTML to display the text message
//        return `<br><button onclick='deleteMessage("${messageId}")'>X</button> <span id='message_${messageId}'><b>${username}</b>: ${message}</span>`;
//    }
//}


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

//function arrayBufferToBinaryString(buffer) {
//    const bytes = new Uint8Array(buffer);
//    let binaryString = 'b"';
//    for (let i = 0; i < bytes.length; i++) {
//        binaryString += '\\x' + bytes[i].toString(16).padStart(2, '0');
//    }
//    binaryString += '"';
//    console.log(binaryString)
//    return binaryString;
//}

function sendChat() {
    const chatTextBox = document.getElementById("postbox");
    const fileInput = document.getElementById('file');

    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws) {
        // Using WebSockets
//        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
//        console.log("ws")
        if (fileInput.files.length > 0 && message) {
        // If both file and message are provided, send both
            const file = fileInput.files[0];
            console.log(file)
            const formData = new FormData();
            formData.append('file', file);

            const reader = new FileReader();
            reader.onload = function(event) {
                const imageBase64 = event.target.result;
                const messageType = "imageText"; // Indicate that this is an image message
                const data = JSON.stringify({"messageType": messageType, "message": message, "image": imageBase64});
                socket.send(data);
            };
            reader.readAsDataURL(file);
        } else if (fileInput.files.length > 0) {
            // If only file is provided, send the image
            const file = fileInput.files[0];
            console.log(file)

            const formData = new FormData();
            formData.append('file', file);

            const reader = new FileReader();
            reader.onload = function(event) {
                const imageBase64 = event.target.result;
                const messageType = "image"; // Indicate that this is an image message
                const data = JSON.stringify({"messageType": messageType, "image": imageBase64});
                console.log(data)
                socket.send(data);
            };
            reader.readAsDataURL(file);
        } else if (message) {
            // If only message is provided, send the message
            const messageType = "chatMessage"; // Indicate that this is a text message
            const data = JSON.stringify({"messageType": messageType, "message": message});
            console.log(data)
            socket.send(data);
        } else {
            // Handle the case where neither a file nor a message is provided
            console.log("Please select a file or enter a message.");
        }

    } else {
        // Using AJAX
        console.log("ajax")
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log(this.response);
            }
        }
        const messageJSON = {"message": message};
        request.open("POST", "/chat-messages");
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

function welcome() {
//    document.addEventListener("keypress", function (event) {
//        if (event.code === "Enter") {
//            sendChat();
//        }
//    });
    const textarea = document.getElementById('postbox'); // Replace 'myTextarea' with the actual ID of your textarea element

    textarea.addEventListener("keypress", function (event) {
        // Check if the Enter key is pressed
        if (event.key === "Enter") {
            // Prevent the default behavior of the Enter key (submitting the form)
            event.preventDefault();

            // Append a newline character to the textarea's value
            this.value += '\n';
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

