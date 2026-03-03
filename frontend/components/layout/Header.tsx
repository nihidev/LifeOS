"use client"

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
  "/appointments": "Appointments",
}

export function Header() {
  const pathname = usePathname()
  const title = routeTitles[pathname] ?? "LifeOS"
  const today = formatDate(new Date())

  return (
    <header className="flex items-center justify-between border-b px-6 py-4">
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{today}</p>
      </div>
    </header>
  )
}
