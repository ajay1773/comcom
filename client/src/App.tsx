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
        <div className="app-container w-full h-screen pr-6 py-6">
          <Routes>
            {/* Default route - redirect to new chat */}
            <Route path="/" element={<Navigate to="/chat" replace />} />

            {/* New chat route */}
            <Route path="/chat" element={<Chat />} />

            {/* Specific conversation route */}
            <Route path="/chat/:conversationId" element={<Chat />} />

            {/* Catch all other routes and redirect to new chat */}
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Routes>
          <Toaster />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
