import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import Cookies from 'js-cookie';

const DataContext = createContext();

const SAMPLE_LOCAL_DATA = require('./local_data_example.json');
const USE_LOCAL_DATA = false;

function createWebSocketUrl(user_data, access_token) {
  return `ws://localhost:8000/ws/${user_data}/${access_token}`;
  // return `http://ec2-3-141-106-24.us-east-2.compute.amazonaws.com:8000/ws/${user_data}/${access_token}`;
}

export const DataProvider = ({ children }) => {
  const [userInfo, setUserInfo] = useState(null);
  const [data, setData] = useState({ chat: [], events: [], todo: [] });
  const [multiUserData, setUserData] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  const connectToSocket = () => {
    if (!userInfo) {
      console.log("User is not logged in");
      return false;
    }
    socketRef.current = new WebSocket(createWebSocketUrl(userInfo.email, userInfo.accessToken));
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
        setTimeout(() => {
          console.log("Retrying WebSocket connection...");
          connectToSocket();
        }, 2000);
      };

      return () => {
        console.log("User changed, closing websocket");
        socketRef.current.close();
      };
    }
  }, [userInfo]);

  const addMessage = (message) => {
    const newMessage = { role: "user", content: message };
    setData((prevData) => {
      // Add user message and empty assistant response
      let updatedChat = [...prevData.chat, newMessage, {
        role: "assistant",
        content: "",
      }];
      // Send the message to the server if connected
      if (socketRef.current && isConnected) {
        const messagePayload = JSON.stringify({ newMessage: message });
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

  const logout = () => {
    Cookies.remove('userInfo');
    setUserInfo(null);
  };

  // Provide the state and functions to children components
  return (
    <DataContext.Provider value={{ data, addMessage, userInfo, setUserInfo, logout }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the DataContext
export const useDataContext = () => useContext(DataContext);
