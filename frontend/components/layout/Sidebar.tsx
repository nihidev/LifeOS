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
  X,
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

interface SidebarProps {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex h-[100dvh] w-64 flex-col border-r bg-background px-3 transition-transform duration-200 md:relative md:translate-x-0 md:z-auto",
        "safe-top",
        open ? "translate-x-0" : "-translate-x-full"
      )}
    >
      <div className="mb-6 flex items-center justify-between px-3 pt-4">
        <h1 className="text-xl font-bold">LifeOS</h1>
        <button
          className="rounded-md p-1.5 text-muted-foreground hover:bg-accent md:hidden"
          onClick={onClose}
          aria-label="Close menu"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
      <nav className="flex flex-1 flex-col gap-1 pb-6">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            onClick={onClose}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-3 text-sm font-medium transition-colors",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <Icon className="h-5 w-5 shrink-0" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}
