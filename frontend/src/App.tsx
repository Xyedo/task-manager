import { Routes, Route } from "react-router";
import Login from "@/pages/Login";
import Home from "@/pages/Home";
import "@/app.css";

function App() {

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />

      <Route path="/:workspaceName" element={<Home />} />
    </Routes>
  );
}

export default App;
