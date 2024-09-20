import React from 'react';
import { useDataContext } from "./DataProvider";

const Header = () => {
  const { logout } = useDataContext();
  return (
    <div>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default Header;
