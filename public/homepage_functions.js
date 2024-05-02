const ws = true;
let socket = null;
var userList = [];
let ImageUrl = "public/image/placeholder_user.jpg";

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
    //---Profile Section---//

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

    function fetchAndPopulateImages(directory, imageGrid) {
        fetch(`/public/${directory}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(function(image) {
                    var button = document.createElement("div"); // Create a <div> element
                    button.classList.add("imageButton"); // Add a class for styling
                    button.style.backgroundImage = `url('/public/${directory}/${image}')`; // Set background image
                    button.addEventListener("click", function() {
                        // Remove glowing effect from previously selected buttons
                        var allButtons = document.querySelectorAll(".imageButton");
                        allButtons.forEach(btn => {
                            btn.classList.remove("selected_starter_image");
                        });

                        // Add glowing effect to the clicked button
                        button.classList.add("selected_starter_image");


                        // Send message to backend and update ImageUrl
                        sendMessageToBackend(directory, image);
                    });
                    imageGrid.appendChild(button);
                });
            })
            .catch(error => console.error("Error fetching image files:", error));
    }

    function sendMessageToBackend(directory, image) {
        // Replace this with your logic to send a message to the backend
        console.log(`Clicked image in directory ${directory}: ${image}`);

        // Construct the URL of the clicked image
        const imageURL = `public/${directory}/${image}`;

        // Update the ImageUrl constant with the clicked image URL
        ImageUrl = imageURL;
    }

    fetchAndPopulateImages("image_grass", imageGridGrass);
    fetchAndPopulateImages("image_fire", imageGridFire);
    fetchAndPopulateImages("image_water", imageGridWater);

    //---Pokecoin Section---//

    document.getElementById('earn-coins-button').addEventListener('click', earnCoins);

});



function earnCoins() {
    fetch('/earn-coins', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('coin-count').textContent = 'PokeCoins: ' + data.new_coin_count;
            alert('PokeCoins earned: ' + data.coins_earned);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while trying to earn coins.');
    });
}

function handleButtonClick() {
    var button = document.getElementById("earn-coins-button");
    var lastClickTime = localStorage.getItem("lastClickTime");
    var currentTime = Date.now();

    // Check if the button was clicked within the last minute
    if (lastClickTime && (currentTime - lastClickTime < 60000)) {
        alert("Please wait before clicking again.");
        return;
    }

    // Store the current time when the button is clicked
    localStorage.setItem("lastClickTime", currentTime);

    // Proceed with the timer logic
    button.disabled = true; // Disable the button
    var count = 60; // Countdown time in seconds
    var timer = setInterval(function() {
        var timerText = document.getElementById("timerText");
        timerText.innerHTML = "Please wait " + count + " seconds for more Pokecoins";
        count--;
        if (count < 0) {
            clearInterval(timer);
            timerText.innerHTML = ""; // Clear the timer text
            button.disabled = false; // Re-enable the button
        }
    }, 1000); // Update every second
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

function chatMessageHTML(messageJSON) {
    console.log(messageJSON);
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    const profilePic = messageJSON.profilePic;
    console.log(messageJSON.id);
    console.log(messageJSON.profilePic)

    // Create an image element with the placeholder image
    let messageHTML = "<img src='" + profilePic + "' alt='Profile Picture' class='ProfilePic'/> ";

    // Append the message content
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

    if (fileInput.files.length > 0 && fileInput.files[0].size > 5500 * 1024) {
            // Check if file size exceeds 5500 KB (5.5 MB)
            console.log("File size exceeds the limit.");
            window.alert("File size exceeds the limit.");
            return;
        }


    if (ws) {
        if (fileInput.files.length > 0 && message) {
            // If both file and message are provided, send both
            const file = fileInput.files[0];

            const formData = new FormData();
            formData.append('file', file);

            const reader = new FileReader();
            reader.onload = function(event) {
                const imageBase64 = event.target.result;
                const messageType = "imageText"; // Indicate that this is an image message
                const data = JSON.stringify({
                    "messageType": messageType,
                    "message": message,
                    "image": imageBase64,
                    "profilePic": ImageUrl // Set the profile picture here
                });
                socket.send(data);
            };
            reader.readAsDataURL(file);
        } else if (fileInput.files.length > 0) {
            // If only file is provided, send the image
            const file = fileInput.files[0];

            const formData = new FormData();
            formData.append('file', file);

            const reader = new FileReader();
            reader.onload = function(event) {
                const imageBase64 = event.target.result;
                const messageType = "image"; // Indicate that this is an image message
                const data = JSON.stringify({
                    "messageType": messageType,
                    "image": imageBase64,
                    "profilePic": ImageUrl // Set the profile picture here
                });
                socket.send(data);
            };
            reader.readAsDataURL(file);
        } else if (message) {
            // If only message is provided, send the message
            const messageType = "chatMessage"; // Indicate that this is a text message
            const data = JSON.stringify({
                "messageType": messageType,
                "message": message,
                "profilePic": ImageUrl // Set the profile picture here
            });
            socket.send(data);
        } else {
            // Handle the case where neither a file nor a message is provided
            console.log("Please select a file or enter a message.");
        }

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