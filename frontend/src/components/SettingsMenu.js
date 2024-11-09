import React, { useEffect } from 'react';

const SettingsMenu = ({ isOpen, setIsOpen }) => {

  const close = () => {
    isOpen = false;
  };

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        console.log("Escape key pressed");
        setIsOpen(false);
      }
    };

    // Add event listener when component mounts
    document.addEventListener('keydown', handleEscape);

    // Remove event listener when component unmounts
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };

  }, []);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', // Changed to fixed to cover full viewport
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.3)', // Semi-transparent black scrim
      display: 'flex',
      alignItems: 'flex-start', // Align to top
      justifyContent: 'flex-end', // Align to right
      paddingTop: '10%', // Push menu down by 10%
      paddingRight: '60px',
      zIndex: 1000,
    }}>
      <div style={{ position: 'relative' }}>
        <button
          onClick={close}
          style={{
            position: 'absolute',
            top: 0,
            right: 0,
            padding: '5px 10px',
            background: 'none',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          ✕
        </button>
        <div>Settings Menu</div>
        <ul style={{ listStyle: 'none', padding: 0, margin: '10px 0' }}>
          <li style={{ padding: '5px 0' }}>Setting 1</li>
          <li style={{ padding: '5px 0' }}>Setting 2</li>
          <li style={{ padding: '5px 0' }}>Setting 3</li>
        </ul>
      </div>
    </div>
  );
};

export default SettingsMenu;
