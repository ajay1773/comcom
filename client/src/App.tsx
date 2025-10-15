import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Chat from "./features/chat";
import { ThemeProvider } from "./contexts/theme-context";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Router>
        <Routes>
          {/* Default route - redirect to new chat */}
          <Route path="/" element={<Navigate to="/chat" replace />} />

          {/* New chat route - always empty window */}
          <Route path="/chat" element={<Chat />} />

          {/* Specific conversation route with c/ prefix */}
          <Route path="/chat/c/:chatId" element={<Chat />} />

          {/* Catch all other routes and redirect to new chat */}
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
        <Toaster />
      </Router>
    </ThemeProvider>
  );
}

export default App;
