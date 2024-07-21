function sendUserMessage() {
    var userInput = document.getElementById("user-input").value;
    var chatBox = document.getElementById("chat-box");

    var userMessage = document.createElement("p");
    userMessage.innerHTML = '<strong>You:</strong> ' + userInput;
    userMessage.style.textAlign = "right";
    userMessage.style.marginBottom = "5px";
    chatBox.appendChild(userMessage);

    document.getElementById("user-input").value = "";

    
    $.ajax({
        url: '/get_response',  
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({message: userInput}),
        success: function(response) {
            var botMessage = document.createElement("p");
            botMessage.innerHTML = '<strong>Healthcare ChatBot:</strong> ' + response.message;
            chatBox.appendChild(botMessage);
            chatBox.scrollTop = chatBox.scrollHeight;  
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}
