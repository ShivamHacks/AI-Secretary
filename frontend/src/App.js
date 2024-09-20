import React, { useState, useEffect } from "react";
import Cookies from 'js-cookie';
import Calendar from './components/Calendar';
import Chat from './components/Chat';
import Todo from './components/Todo';
import Header from './components/Header';
import Auth from './components/Auth';
import { DataProvider } from "./components/DataProvider";

const verifyAccessToken = async (accessToken) => {
  try {
    const response = await fetch(`https://oauth2.googleapis.com/tokeninfo?access_token=${accessToken}`);
    const data = await response.json();
    if (data.error) {
      console.error('Invalid Access Token:', data.error_description);
      return false;
    } else {
      console.log('Valid Access Token:', data);
      return true;
    }
  } catch (error) {
    console.error('Error verifying access token:', error);
    return false;
  }
};

function App() {
  const [token, setToken] = useState(null);

  // Check if there is an access token stored
  useEffect(() => {
    const storedToken = Cookies.get("accessToken");
    if (storedToken && verifyAccessToken(storedToken)) {
      setToken(storedToken);
    }
  }, []);

  return (
    <div>
      {
        token ? (
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
                <Header />
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
          <Auth setToken={setToken} />
        )
      }
    </div>
  );
}

export default App;
