import Chat from "./features/chat";
import { ThemeProvider } from "./contexts/theme-context";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="app-container w-full h-screen pr-6 py-6">
        <Chat />
      </div>
    </ThemeProvider>
  );
}

export default App;
