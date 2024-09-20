import React from "react";
import AppLayout from './components/AppLayout';
import { DataProvider } from "./components/DataProvider";

function App() {
  return (
    <DataProvider>
      <AppLayout />
    </DataProvider >
  );
}

export default App;
