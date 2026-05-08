"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Trophy,
  Dumbbell,
  CreditCard,
  UtensilsCrossed,
} from "lucide-react"
import { cn } from "@/lib/utils"

const items = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/small-wins", label: "Wins", icon: Trophy },
  { href: "/workout", label: "Workout", icon: Dumbbell },
  { href: "/food", label: "Food", icon: UtensilsCrossed },
  { href: "/expenses", label: "Expenses", icon: CreditCard },
]

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav className="safe-bottom fixed bottom-0 left-0 right-0 z-30 flex border-t bg-background md:hidden">
      {items.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(href + "/")
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex flex-1 flex-col items-center gap-1 py-2.5 text-[10px] font-medium transition-colors",
              active ? "text-primary" : "text-muted-foreground"
            )}
          >
            <Icon className="h-5 w-5" />
            {label}
          </Link>
        )
      })}
    </nav>
  )
}
