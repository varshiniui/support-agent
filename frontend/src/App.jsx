import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./AuthContext";
import AuthPage from "./pages/AuthPage";
import Home from "./pages/Home";

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="muted center">Loading...</p>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      <Route path="/" element={<Protected><Home /></Protected>} />
    </Routes>
  );
}