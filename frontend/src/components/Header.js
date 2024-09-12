import React, { useState } from 'react';
import { useDataContext } from "./DataProvider";

const Header = () => {
  const { setUser } = useDataContext();
  const [message, setMessage] = useState('');

  const sendMessage = () => {
    setUser(message);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      sendMessage(); // Call send message function when Enter is pressed
    }
  };

  return (
    <div>
      <button onClick={sendMessage}>Set User</button>
      <input
        type="text"
        value={message}
        onChange={e => setMessage(e.target.value)}
        onKeyDown={handleKeyDown} // Add this to capture Enter key press
      />
    </div>
  );
};

export default Header;
