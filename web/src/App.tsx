import { BrowserRouter, Route, Routes } from "react-router-dom"
import Shell from "@/components/Shell"
import Dashboard from "@/pages/Dashboard"
import SearchPage from "@/pages/SearchPage"
import Chat from "@/pages/Chat"
import Profile from "@/pages/Profile"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Shell />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
