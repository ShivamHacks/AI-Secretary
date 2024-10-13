import React, { useState } from 'react';
import { useDataContext } from "./DataProvider";
import './component_styles.css';

const Header = () => {
  const { logout, sendFeedback } = useDataContext();
  const [feedback, setFeedback] = useState("");

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      sendFeedback(feedback);
      setFeedback('');
    }
  };

  const handleSendFeedback = () => {
    const newFeedback = feedback.trim();
    if (newFeedback) {
      sendFeedback(newFeedback);
      setFeedback('');
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingBottom: '10px',
    }}>
      <h1 style={{
        margin: '0 20px 0 0'
      }}>
        AI Secretary
      </h1>
      <input
        type="text"
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
        onKeyDown={handleKeyDown} // Add this to capture Enter key press
        placeholder="Please share any feedback, ideas, and issues here! Type 'enter' to submit."
      />
      <button onClick={handleSendFeedback} style={{ marginRight: '10px' }}>Send</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default Header;
