"use client"

import { Menu } from "lucide-react"
import { formatDate } from "@/lib/utils"
import { usePathname } from "next/navigation"

const routeTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/small-wins": "Small Wins",
  "/workout": "Workout",
  "/self-assessment": "Self Assessment",
  "/expenses": "Expenses",
  "/resolutions": "Resolutions",
  "/food": "Food Log",
  "/grocery": "Grocery List",
}

interface HeaderProps {
  onMenuToggle: () => void
}

export function Header({ onMenuToggle }: HeaderProps) {
  const pathname = usePathname()
  const title = routeTitles[pathname] ?? "LifeOS"
  const today = formatDate(new Date())

  return (
    <header className="safe-top flex items-center gap-3 border-b bg-background px-4 py-3 md:px-6 md:py-4">
      <button
        className="rounded-md p-1.5 text-muted-foreground hover:bg-accent md:hidden"
        onClick={onMenuToggle}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>
      <div>
        <h2 className="text-lg font-semibold leading-tight">{title}</h2>
        <p className="text-xs text-muted-foreground">{today}</p>
      </div>
    </header>
  )
}
