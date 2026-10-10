import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import TopBar from "./TopBar"

export default function Shell() {
  return (
    <div className="min-h-dvh bg-bg">
      <Sidebar />
      <TopBar />
      <main className="glow min-h-dvh lg:pl-sidebar">
        <div className="mx-auto max-w-main px-5 py-6 sm:px-8 sm:py-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
