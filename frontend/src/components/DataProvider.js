import React, { createContext, useContext, useState, useEffect, useRef } from "react";

const DataContext = createContext();

const SAMPLE_LOCAL_DATA = require('./local_data_example.json');
const SOCKET_URL = "ws://localhost:8000/ws";
const USE_LOCAL_DATA = true;

export const DataProvider = ({ children }) => {
  const [data, setData] = useState({ chat: [], events: [], todo: [] });
  const [multiUserData, setUserData] = useState({});
  const [currentUser, setCurrentUser] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (USE_LOCAL_DATA) {
      setData(SAMPLE_LOCAL_DATA);
      setIsConnected(false); // No connection, since local data is used
    } else {
      socketRef.current = new WebSocket(SOCKET_URL);

      socketRef.current.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
      };

      socketRef.current.onmessage = (event) => {
        try {
          const receivedData = JSON.parse(event.data);
          if (
            receivedData &&
            Array.isArray(receivedData.chat) &&
            Array.isArray(receivedData.events) &&
            Array.isArray(receivedData.todo)
          ) {
            // Override the local state with the server data
            setData(receivedData);
          } else {
            console.error("Received invalid data format");
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
        socketRef.current.close();
      };
    }
  }, []);

  const setUser = (user) => {
    console.log(`Switching user from ${currentUser} to: ${user}`);
    if (currentUser !== user) {
      // Save the current user data before switching
      setUserData((userData) => {
        userData[currentUser] = data;
        return userData;
      });
      // Switch the user and load their data
      setCurrentUser(user);
      setData(multiUserData[user] || { chat: [], events: [], todo: [] });
    }
  };

  const addMessage = (message) => {
    const newMessage = { role: "user", content: message };
    setData((prevData) => {
      let updatedChat = [...prevData.chat, newMessage];
      if (USE_LOCAL_DATA) {
        updatedChat = [...updatedChat, {
          role: "assistant",
          content: `You typed "${message}"`,
        }];
      } else if (socketRef.current && isConnected) {
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

  // Provide the state and functions to children components
  return (
    <DataContext.Provider value={{ data, isConnected, addMessage, setUser }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the DataContext
export const useDataContext = () => useContext(DataContext);
