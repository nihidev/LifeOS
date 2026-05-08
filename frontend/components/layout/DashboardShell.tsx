"use client"

import { useState } from "react"
import { Sidebar } from "./Sidebar"
import { Header } from "./Header"
import { PageWrapper } from "./PageWrapper"
import { BottomNav } from "./BottomNav"

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-[100dvh] overflow-hidden">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex flex-1 flex-col overflow-auto">
        <Header onMenuToggle={() => setSidebarOpen((o) => !o)} />
        <PageWrapper>{children}</PageWrapper>
      </div>
      <BottomNav />
    </div>
  )
}
