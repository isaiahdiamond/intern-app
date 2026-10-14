import { BrowserRouter, Route, Routes } from "react-router-dom";
import Shell from "@/components/Shell";
import Chat from "@/pages/Chat";
import Dashboard from "@/pages/Dashboard";
import Listings from "@/pages/Listings";
import Onboarding from "@/pages/Onboarding";
import Profile from "@/pages/Profile";
import Tracker from "@/pages/Tracker";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Shell />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/listings" element={<Listings />} />
          <Route path="/tracker" element={<Tracker />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Profile />} />
          <Route path="/onboarding" element={<Onboarding />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
