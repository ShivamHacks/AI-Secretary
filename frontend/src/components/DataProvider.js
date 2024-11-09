import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import Cookies from 'js-cookie';

const DataContext = createContext();

const SAMPLE_LOCAL_DATA = require('./local_data_example.json');
const USE_LOCAL_DATA = false;

export const DataProvider = ({ children }) => {
  const [userInfo, setUserInfo] = useState(null);
  const [data, setData] = useState({ chat: [], events: [], todo: [] });
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  const isWindowLocalhost = window.location.hostname === "localhost";
  const [isLocalhost, setIsLocalhost] = useState(isWindowLocalhost);

  const getWebSocketUrl = (user_data, access_token) => {
    if (isLocalhost) {
      return `ws://localhost:8000/ws/${user_data}/${access_token}`;
    } else {
      return `wss://managemytimeai.com/ws/${user_data}/${access_token}`;
    }
  };

  const getBaseUrl = () => {
    return isLocalhost ? "http://localhost:8000" : "https://managemytimeai.com";
  };

  const logCreateMessageEvent = (userId) => {
    const cujId = Math.random().toString(36).substring(2, 15);
    fetch(`${getBaseUrl()}/analytics`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cuj_id: cujId,
        event_type: 'message_sent_from_frontend',
        timestamp: new Date().toISOString(),
        user_id: userId,
      })
    });
    return cujId;
  }

  const connectToSocket = () => {
    if (!userInfo) {
      console.log("User is not logged in");
      return false;
    }
    console.log("Connecting to WebSocket, isLocalhost:", isLocalhost);
    socketRef.current = new WebSocket(getWebSocketUrl(userInfo.email, userInfo.accessToken));
    return true;
  };

  useEffect(() => {
    if (USE_LOCAL_DATA) {
      setData(SAMPLE_LOCAL_DATA);
      setIsConnected(false); // No connection, since local data is used
    } else {
      if (!connectToSocket()) {
        console.log("WebSocket connection not established");
        return;
      }

      socketRef.current.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
      };

      socketRef.current.onmessage = (event) => {
        try {
          const receivedData = JSON.parse(event.data);
          if (receivedData.type === 'chunk') {
            // Handle the streamed message chunk (partial message)
            setData((prevData) => {
              // Find the last message and update its content if it's partial
              const updatedChat = [...prevData.chat];
              const lastMessageIndex = updatedChat.length - 1;
              if (lastMessageIndex == 0) {
                return prevData;
              }
              updatedChat[lastMessageIndex].content += receivedData.chunk;
              return {
                ...prevData,
                chat: updatedChat
              };
            });
          } else if (receivedData.type === 'final') {
            // Handle the final updated data after the stream is done
            setData(() => {
              return receivedData.data;
            });
          } else if (receivedData.type === 'feedback_confirmation') {
            alert(`Feedback submitted: ${receivedData.feedback}`)
          } else {
            console.error("Received unknown data type");
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      socketRef.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      socketRef.current.onclose = () => {
        console.log("WebSocket connection closed");
        setIsConnected(false);
      };

      return () => {
        console.log("State changed, closing websocket");
        socketRef.current.close();
      };
    }
  }, [userInfo, isLocalhost]);

  const addMessage = (message) => {
    setData((prevData) => {
      // Add user message and empty assistant response
      let updatedChat = [...prevData.chat, {
        role: "user",
        content: message,
      }, {
        role: "assistant",
        content: "",
      }];
      // Send the message to the server if connected
      if (socketRef.current && isConnected) {
        const cujID = logCreateMessageEvent(userInfo.email);
        const messagePayload = JSON.stringify({
          newMessage: message,
          cujID: cujID,
        });
        console.log("Sending message to server:", messagePayload);
        socketRef.current.send(messagePayload);
      } else {
        console.log("WebSocket is not connected. Message only added locally.");
      }

      return {
        ...prevData,
        chat: updatedChat,
      };
    });
  };

  const sendFeedback = (feedback) => {
    if (socketRef.current && isConnected) {
      const feedbackPayload = JSON.stringify({ feedback: feedback });
      console.log("Sending feedback to server:", feedbackPayload);
      socketRef.current.send(feedbackPayload);
    } else {
      // TODO: make this an error message
      console.log("WebSocket is not connected. Could not send feedback");
    }
  };

  const logout = () => {
    Cookies.remove('userInfo');
    setUserInfo(null);
  };

  // Provide the state and functions to children components
  return (
    <DataContext.Provider value={{
      data,
      addMessage,
      userInfo,
      setUserInfo,
      logout,
      sendFeedback,
      isLocalhost,
      setIsLocalhost,
    }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the DataContext
export const useDataContext = () => useContext(DataContext);
