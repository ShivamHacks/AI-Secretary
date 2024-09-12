import React, { createContext, useContext, useState, useEffect } from "react";

const DataContext = createContext();

const SAMPLE_LOCAL_DATA = require('./local_data_example.json');
const SOCKET_URL = "ws://localhost:8000/ws";
const USE_LOCAL_DATA = true;

export const DataProvider = ({ children }) => {
  const [data, setData] = useState({ chat: [], events: [], todo: [] });
  const [isConnected, setIsConnected] = useState(false);

  const addMessage = (message) => {
    const newMessage = { role: "user", content: message };
    setData((prevData) => {
      let updatedChat = [...prevData.chat, newMessage];
      if (USE_LOCAL_DATA) {
        updatedChat = [...updatedChat, {
          role: "assistant",
          content: `You typed "${message}"`,
        }];
      }

      return {
        ...prevData,
        chat: updatedChat,
      };
    });
  };

  useEffect(() => {
    if (USE_LOCAL_DATA) {
      setData(SAMPLE_LOCAL_DATA);
      setIsConnected(false); // No connection, since local data is used
    } else {
      const socket = new WebSocket(SOCKET_URL);

      socket.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
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

      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed");
        setIsConnected(false);
      };

      return () => {
        socket.close();
      };
    }
  }, []);

  // Provide the state and functions to children components
  return (
    <DataContext.Provider value={{ data, isConnected, addMessage }}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to use the DataContext
export const useDataContext = () => useContext(DataContext);
