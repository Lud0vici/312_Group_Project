const ws = true;
let socket = null;
var userList = [];

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('wss://' + window.location.host + '/websocket');
    //    socket = new WebSocket('wss://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType

        if(messageType === 'userList'){
            //console.log(message.users)
            updateUserList(message.users)
        } else {
            //console.log(ws_message.data)
            //const message = JSON.parse(ws_message.data);
            //console.log(message)
            //const messageType = message.messageType
            //console.log(messageType)
            addMessageToChat(message)
        }
    }
}

function updateUserList(userList) {
    var userListElement = document.getElementById("userList");
    // Clear the existing user list
    userListElement.innerHTML = "";
    // Add each user from the updated user list to the user lit on html
    userList.forEach(function(user) {
        var listItem = document.createElement("li");
        listItem.textContent = user;
        userListElement.appendChild(listItem);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // Show and hide the popup
    document.getElementById("openPopupBtn").addEventListener("click", function() {
        document.getElementById("popup").style.display = "block";
    });

    document.getElementById("closePopupBtn").addEventListener("click", function() {
        document.getElementById("popup").style.display = "none";
    });

    // Dynamically create and display profile pictures/starters in the popup
    var imageGridGrass = document.getElementById("imageGridGrass");
    var imageGridFire = document.getElementById("imageGridFire");
    var imageGridWater = document.getElementById("imageGridWater");

    // function fetchAndPopulateImages(directory, imageGrid) {
    //     fetch(`/public/${directory}`)
    //         .then(response => response.json())
    //         .then(data => {
    //             data.forEach(function(image) {
    //                 var img = document.createElement("img");
    //                 img.src = `/public/${directory}/${image}`;
    //                 imageGrid.appendChild(img);
    //             });
    //         })
    //         .catch(error => console.error("Error fetching image files:", error));
    // }

    function fetchAndPopulateImages(directory, imageGrid) {
        fetch(`/public/${directory}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(function(image) {
                    var button = document.createElement("div"); // Create a <div> element
                    button.classList.add("imageButton"); // Add a class for styling
                    button.style.backgroundImage = `url('/public/${directory}/${image}')`; // Set background image
                    button.addEventListener("click", function() {
                        // Send message to backend
                        sendMessageToBackend(directory, image); // Replace with actual function
                    });
                    imageGrid.appendChild(button);
                });
            })
            .catch(error => console.error("Error fetching image files:", error));
    }

    function sendMessageToBackend(directory, image) {
        // Replace this with your logic to send a message to the backend
        console.log(`Clicked image in directory ${directory}: ${image}`);
    }

    fetchAndPopulateImages("image_grass", imageGridGrass);
    fetchAndPopulateImages("image_fire", imageGridFire);
    fetchAndPopulateImages("image_water", imageGridWater);
});











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
//    let messageHTML = "<profile-pic placeholder> ";
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
    const chatTextBox = document.getElementById("postbox");
    const fileInput = document.getElementById('file');

    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws) {
        // Using WebSockets
//        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
//        console.log("ws")
        if (fileInput.files.length > 0 && fileInput.files[0].size > 10000 * 1024) {
            // Check if file size exceeds 10,000 KB (10 MB)
            console.log("File size exceeds the limit.");
            window.alert("File size exceeds the limit of 10,000 KB.");
            return;
        }

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

