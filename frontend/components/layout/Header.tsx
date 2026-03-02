"use client"

import { signOut } from "@/lib/auth"
import { formatDate } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

interface HeaderProps {
  title: string
}

export function Header({ title }: HeaderProps) {
  const router = useRouter()
  const today = formatDate(new Date())

  async function handleSignOut() {
    await signOut()
    router.push("/login")
  }

  return (
    <header className="flex items-center justify-between border-b px-6 py-4">
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{today}</p>
      </div>
      <Button variant="outline" size="sm" onClick={handleSignOut}>
        Sign out
      </Button>
    </header>
  )
}
