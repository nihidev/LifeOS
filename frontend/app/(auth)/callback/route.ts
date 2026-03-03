import { NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get("code")
  const errorParam = searchParams.get("error")
  const errorDesc = searchParams.get("error_description")

  console.log("[callback] incoming URL:", request.url)
  console.log("[callback] code:", code ? `${code.slice(0, 12)}…` : "MISSING")
  console.log("[callback] error param:", errorParam, errorDesc)

  if (errorParam) {
    console.error("[callback] Supabase error:", errorParam, errorDesc)
    return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(errorDesc ?? errorParam)}`)
  }

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    console.log("[callback] exchangeCodeForSession error:", error?.message ?? "none")
    if (!error) {
      return NextResponse.redirect(`${origin}/dashboard`)
    }
    return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(error.message)}`)
  }

  console.warn("[callback] no code param — check Supabase redirect URL config")
  return NextResponse.redirect(`${origin}/login?error=no_code`)
}
