"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Trophy,
  Dumbbell,
  Brain,
  CreditCard,
  Target,
  UtensilsCrossed,
  ShoppingCart,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/small-wins", label: "Small Wins", icon: Trophy },
  { href: "/workout", label: "Workout", icon: Dumbbell },
  { href: "/self-assessment", label: "Self Assessment", icon: Brain },
  { href: "/expenses", label: "Expenses", icon: CreditCard },
  { href: "/resolutions", label: "Resolutions", icon: Target },
  { href: "/food", label: "Food", icon: UtensilsCrossed },
  { href: "/grocery", label: "Grocery", icon: ShoppingCart },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex h-screen w-60 flex-col border-r bg-background px-3 py-6">
      <div className="mb-6 px-3">
        <h1 className="text-xl font-bold">LifeOS</h1>
      </div>
      <nav className="flex flex-1 flex-col gap-1">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}
