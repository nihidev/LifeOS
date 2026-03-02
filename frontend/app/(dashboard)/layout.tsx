import { redirect } from "next/navigation"
import { createClient } from "@supabase/supabase-js"
import { cookies } from "next/headers"
import { Sidebar } from "@/components/layout/Sidebar"
import { Header } from "@/components/layout/Header"
import { PageWrapper } from "@/components/layout/PageWrapper"

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      auth: { persistSession: false },
      global: { headers: { Cookie: cookieStore.toString() } },
    }
  )

  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    redirect("/login")
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-auto">
        <Header title="LifeOS" />
        <PageWrapper title="LifeOS">{children}</PageWrapper>
      </div>
    </div>
  )
}
