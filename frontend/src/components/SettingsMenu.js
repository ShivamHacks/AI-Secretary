import React, { useEffect } from 'react';

// TODO: this could be a generic floating menu component
const SettingsMenu = ({ isOpen, setIsOpen }) => {

  const close = () => {
    setIsOpen(false);
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      close();
    }
  };

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        close();
      }
    };

    // Add event listener when component mounts
    document.addEventListener('keydown', handleEscape);

    // Remove event listener when component unmounts
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };

  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      onClick={handleBackdropClick}
      style={{
        position: 'fixed', // Changed to fixed to cover full viewport
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.3)', // Semi-transparent black scrim
        paddingTop: '10%', // Push menu down by 10%
        zIndex: 1000,
        display: 'flex',
        justifyContent: 'center',
      }}>
      <div style={{
        position: 'relative',
        width: '50%',
        height: 'fit-content',
        maxHeight: '80%', // Prevent from getting too tall
        overflowY: 'auto', // Allow scrolling if content is very tall
        backgroundColor: 'white',
        borderRadius: '10px',
        padding: '20px',
      }}>
        <button
          onClick={close}
          style={{
            position: 'absolute',
            top: 0,
            right: 0,
            padding: '5px 10px',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'black',
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
