import React, { useEffect } from 'react';
import Calendar from './components/Calendar';
import Chat from './components/Chat';
import Database from './components/Database';
import Todo from './components/Todo';
import { DataProvider } from "./components/DataProvider";

function App() {
  const database = new Database();
  database.loadSampleData();

  return (
    <DataProvider>
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
          <Chat />
        </div>

        <div style={{
          width: '60%',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{
            height: '50%',
          }}>
            <Calendar />
          </div>
          <div style={{
            height: 'calc(50% - 20px)',
            paddingTop: '20px',
          }}>
            <Todo />
          </div>
        </div>
      </div >
    </DataProvider>
  );
}

export default App;