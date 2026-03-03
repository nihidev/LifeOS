import { NextRequest, NextResponse } from "next/server"
import { createServerClient } from "@supabase/ssr"
import { createAdminClient } from "@/lib/supabase/admin"

export async function GET(request: NextRequest) {
  if (process.env.NODE_ENV !== "development") {
    return new NextResponse("Not found", { status: 404 })
  }

  const { origin } = new URL(request.url)
  const email = process.env.DEV_USER_EMAIL!

  // Step 1: Admin generates a one-time OTP for the user (no email sent)
  const admin = createAdminClient()
  const { data: linkData, error: linkError } = await admin.auth.admin.generateLink({
    type: "magiclink",
    email,
  })

  if (linkError || !linkData?.properties?.email_otp) {
    return new NextResponse(
      `Dev login failed (generate): ${linkError?.message ?? "no OTP returned"}`,
      { status: 500 }
    )
  }

  // Step 2: Verify the OTP server-side using a cookie-aware server client
  // This trades the OTP for a real session and writes it into response cookies —
  // no browser PKCE verifier needed.
  const response = NextResponse.redirect(`${origin}/dashboard`)

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )

  const { error: verifyError } = await supabase.auth.verifyOtp({
    email,
    token: linkData.properties.email_otp,
    type: "email",
  })

  if (verifyError) {
    return new NextResponse(
      `Dev login failed (verify): ${verifyError.message}`,
      { status: 500 }
    )
  }

  return response
}
