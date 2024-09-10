import React, { useEffect } from 'react';
import Calendar from './components/Calendar';
import Chat from './components/Chat';
import Database from './components/Database';
import Todo from './components/Todo';

function App() {
  const database = new Database();
  database.loadSampleData();

  // Example WebSocket connection
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');

    // Handle when the WebSocket connection is opened
    socket.onopen = () => {
      console.log('Connection established!');
      socket.send('Hello Server');
    };

    // Handle messages from the server
    socket.onmessage = function (event) {
      console.log('Message from server: ', event.data);
    };

    // Handle WebSocket closing
    socket.onclose = () => {
      console.log('Connection closed');
    };
  }, []);


  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      padding: '20px',
      width: 'calc(100vw - 40px)',
      height: 'calc(100vh - 40px)',
    }}>
      <div style={{
        width: 'calc(40% - 20px)',
        paddingRight: '20px',
      }}>
        <Chat database={database} />
      </div>

      <div style={{
        width: '60%',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{
          height: '50%',
        }}>
          <Calendar database={database} />
        </div>
        <div style={{
          height: 'calc(50% - 20px)',
          paddingTop: '20px',
        }}>
          <Todo database={database} />
        </div>
      </div>
    </div>
  );
}

export default App;