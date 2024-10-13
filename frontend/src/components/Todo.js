import React, { useState, useEffect } from "react";
import { useDataContext } from "./DataProvider";

function TodoList() {
  const { data } = useDataContext();
  const [todos, setTodos] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: "", direction: "" });

  // Function to sort the todos array based on the sort configuration
  const sortTodos = (todosToSort, config) => {
    if (config.key === "") return todosToSort; // No sorting applied yet

    const sortedTodos = [...todosToSort].sort((a, b) => {
      if (a[config.key] < b[config.key]) {
        return config.direction === "ascending" ? -1 : 1;
      }
      if (a[config.key] > b[config.key]) {
        return config.direction === "ascending" ? 1 : -1;
      }
      return 0;
    });

    return sortedTodos;
  };

  // Sync the local todos state with the global data and maintain the sorting order
  useEffect(() => {
    const sortedData = sortTodos([...data.todo], sortConfig); // Reapply sorting based on sortConfig
    setTodos(sortedData);
  }, [data.todo, sortConfig]); // Reapply whenever global data or sortConfig changes

  const sortByColumn = (key) => {
    let direction = "ascending";
    if (sortConfig.key === key && sortConfig.direction === "ascending") {
      direction = "descending";
    }

    setSortConfig({ key, direction }); // Update sortConfig, this will trigger re-sorting
  };

  const getArrow = (column) => {
    if (sortConfig.key !== column || sortConfig.direction === 'neutral') {
      return '⇅'; // Neutral sort indicator (can be adjusted)
    }
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <div style={{ height: '100%', overflowY: 'scroll' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          {/* Sticky header */}
          <thead style={{
            position: 'sticky',
            top: '0',
            zIndex: 1,
            backgroundColor: '#fff',
            boxShadow: '0 2px 2px -1px rgba(0, 0, 0, 0.1)',
          }}>
            <tr style={{ height: '50px' }}>
              {/* For the checkboxes */}
              <th onClick={() => sortByColumn("task")} style={{ width: '60%', cursor: 'pointer' }}>
                Task {getArrow("task")}
              </th>
              <th onClick={() => sortByColumn("deadline")} style={{ width: '20%', cursor: 'pointer' }}>
                Deadline {getArrow("deadline")}
              </th>
              <th onClick={() => sortByColumn("category")} style={{ width: '15%', cursor: 'pointer' }}>
                Category {getArrow("category")}
              </th>
            </tr>
          </thead>
          <tbody>
            {todos.map((todo, index) => (
              <tr key={index} style={{ height: '50px', backgroundColor: index % 2 === 0 ? '#f9f9f9' : '#fff' }}>
                <td>{todo.task}</td>
                <td>{todo.deadline}</td>
                <td>{todo.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TodoList;
