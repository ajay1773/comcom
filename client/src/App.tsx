import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Chat from "./features/chat";
import { ThemeProvider } from "./contexts/theme-context";
import { Toaster } from "@/components/ui/sonner";
import { useChatStore } from "@/store/chat-store";

function App() {
  const { isLoggedIn } = useChatStore();
  const loggedIn = isLoggedIn();

  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Router>
        <div
          className={`app-container w-full h-screen ${
            loggedIn
              ? "pr-6 py-6" // Logged in: with sidebar, keep padding
              : "p-6" // Logged out: no sidebar, remove padding for full screen
          }`}
        >
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
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
