import React, { useState, useEffect } from "react";
import Cookies from 'js-cookie';
import Calendar from './components/Calendar';
import Chat from './components/Chat';
import Todo from './components/Todo';
import Header from './components/Header';
import Auth from './components/Auth';
import { DataProvider } from "./components/DataProvider";

function App() {
  const [userInfo, setUserInfo] = useState(null);

  const logout = () => {
    Cookies.remove('userInfo');
    setUserInfo(null);
  };

  return (
    <div>
      {
        userInfo ? (
          <DataProvider>
            <div style={{
              display: 'flex',
              flexDirection: 'column', // Stack header and layout vertically
              padding: '20px',
              width: 'calc(100vw - 40px)',
              height: 'calc(100vh - 40px)', // Full available height
            }}>
              {/* Header Section */}
              <div style={{
                height: '5%',
              }}>
                <Header logout={logout} />
              </div>

              {/* Main Layout Section (Chat, Calendar, Todo) */}
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                height: '95%',
              }}>
                <div style={{
                  width: 'calc(40% - 20px)',
                  paddingRight: '20px',
                }}>
                  <Chat />
                </div> {/* End of chat */}

                <div style={{
                  width: '60%',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}>
                  <div style={{
                    height: '50%',
                  }}>
                    <Calendar />
                  </div> {/* End of calendar */}
                  <div style={{
                    height: 'calc(50% - 20px)',
                    paddingTop: '20px',
                  }}>
                    <Todo />
                  </div> {/* End of todo */}
                </div> {/* End of calendar and todo parent element */}
              </div>
            </div>

          </DataProvider >
        ) : (
          <Auth setUserInfo={setUserInfo} />
        )
      }
    </div>
  );
}

export default App;
