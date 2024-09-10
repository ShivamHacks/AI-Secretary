import React, { useState, useRef } from 'react';

function Chat({ database }) {
  const [currentSender, setCurrentSender] = useState("user"); // Track current sender
  const [inputMessage, setInputMessage] = useState(""); // Track the input message
  const bottomRef = useRef(null); // Create a ref for the bottom of the chat

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const newMessage = {
        message: inputMessage,
        sender: currentSender
      };

      // Update message list and alternate the sender
      database.addChatMessage(newMessage);
      setCurrentSender(prevSender => (prevSender === "user" ? "assistant" : "user"));
      setInputMessage(''); // Clear the input after sending
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage(); // Call send message function when Enter is pressed
      bottomRef.current?.scrollIntoView({ behavior: "smooth" }); // Scroll to the bottom
    }
  };

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div
        style={{
          border: '1px solid #ddd',
          borderRadius: '10px',
          padding: '20px',
          flexGrow: 1,
          overflowY: 'scroll',
        }}
      >
        {database.getChatMessages().map((msg, index) => (
          <div
            key={index}
            style={{
              textAlign: msg.sender === 'user' ? 'right' : 'left',
              marginBottom: '10px'
            }}
          >
            <span
              style={{
                display: 'inline-block',
                padding: '10px',
                backgroundColor: msg.sender === 'user' ? '#0084ff' : '#f0f0f0',
                color: msg.sender === 'user' ? '#fff' : '#000',
                borderRadius: '10px',
                maxWidth: '70%',
                wordWrap: 'break-word'
              }}
            >
              {msg.message}
            </span>
          </div>
        ))}
        <div ref={bottomRef} /> {/* Add this to scroll to the bottom */}
      </div>
      <div style={{
        padding: '10px',
        display: 'flex',
      }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown} // Add this to capture Enter key press
          placeholder="Type a message"
          style={{
            padding: '10px',
            borderRadius: '5px',
            border: '1px solid #ddd',
            marginRight: '10px',
            flexGrow: 1
          }}
        />
        <button
          onClick={handleSendMessage}
          style={{
            padding: '10px 20px',
            borderRadius: '5px',
            backgroundColor: '#0084ff',
            color: '#fff',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
