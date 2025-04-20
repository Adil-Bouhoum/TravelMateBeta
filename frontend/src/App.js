import React, { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([
    {
      role: "system",
      content: "Welcome to TravelMate! How can I help plan your next vacation?",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message to conversation
    const updatedConversation = [
      ...conversation,
      { role: "user", content: message },
    ];
    setConversation(updatedConversation);
    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      // Add bot response to conversation
      setConversation([
        ...updatedConversation,
        { role: "system", content: data.response },
      ]);
    } catch (error) {
      console.error("Error:", error);
      // Add error message to conversation
      setConversation([
        ...updatedConversation,
        {
          role: "system",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>TravelMate</h1>
        <p>Your AI Travel Assistant</p>
      </header>

      <div className="chat-container">
        <div className="messages">
          {conversation.map((msg, index) => (
            <div
              key={index}
              className={`message ${
                msg.role === "user" ? "user-message" : "system-message"
              }`}
            >
              {msg.content}
            </div>
          ))}
          {isLoading && (
            <div className="system-message loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="message-form">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about your travel plans..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
