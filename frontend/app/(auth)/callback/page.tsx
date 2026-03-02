"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { supabase } from "@/lib/auth"

export default function CallbackPage() {
  const router = useRouter()

  useEffect(() => {
    supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_IN" && session) {
        router.push("/dashboard")
      }
    })

    // Handle the hash fragment from magic link
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        router.push("/dashboard")
      }
    })
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <p className="text-muted-foreground">Signing you in…</p>
    </div>
  )
}
