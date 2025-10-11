import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { BrowserRouter } from "react-router";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Auth } from "@/hooks/AuthProvider.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Auth>
        <DndProvider backend={HTML5Backend}>
          <App />
        </DndProvider>
      </Auth>
    </BrowserRouter>
  </StrictMode>
);
