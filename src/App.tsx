import { Routes, Route } from "react-router";
import Login from "@/pages/Login";
import Home from "@/pages/Home";
import "@/app.css"

function App() {
  // simple auth mock using sessionStorage
  const isAuthenticated = Boolean(sessionStorage.getItem("auth"));

  return (
    <Routes>
      <Route
        path="/"
        element={isAuthenticated ? <Home /> : <Login />}
        key={String(isAuthenticated)}
      />
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={isAuthenticated ? <Home /> : <Login />}
        key={String(isAuthenticated)}
      />

      <Route
        path="/:projectName"
        element={isAuthenticated ? <Home /> : <Login />}
        key={String(isAuthenticated)}
      />
    </Routes>
  );
}

export default App;
