import {
  Trophy, Dumbbell, Brain, CreditCard, Target,
  UtensilsCrossed, ShoppingCart, Calendar, TrendingUp,
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const modules = [
  { icon: Trophy,         label: "Small Wins",      href: "/small-wins",       phase: "Phase 1", color: "text-yellow-500" },
  { icon: Dumbbell,       label: "Workout",          href: "/workout",           phase: "Phase 2", color: "text-blue-500"   },
  { icon: Brain,          label: "Self Assessment",  href: "/self-assessment",   phase: "Phase 3", color: "text-purple-500" },
  { icon: CreditCard,     label: "Expenses",         href: "/expenses",          phase: "Phase 4", color: "text-green-500"  },
  { icon: Target,         label: "Resolutions",      href: "/resolutions",       phase: "Phase 5", color: "text-red-500"    },
  { icon: UtensilsCrossed,label: "Food Log",         href: "/food",              phase: "Phase 8", color: "text-orange-500" },
  { icon: ShoppingCart,   label: "Grocery List",     href: "/grocery",           phase: "Phase 8", color: "text-teal-500"   },
  { icon: Calendar,       label: "Appointments",     href: "/appointments",      phase: "Phase 8", color: "text-pink-500"   },
]

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold">Welcome to LifeOS</h1>
        <p className="text-muted-foreground">Your personal discipline and accountability dashboard.</p>
      </div>

      {/* Status banner */}
      <div className="flex items-center gap-3 rounded-lg border bg-muted/40 p-4">
        <TrendingUp className="h-5 w-5 text-primary" />
        <div className="text-sm">
          <span className="font-medium">Phase 0 complete</span>
          <span className="text-muted-foreground"> — foundation is live. Feature phases are rolling out next.</span>
        </div>
        <Badge className="ml-auto">Build in progress</Badge>
      </div>

      {/* Module grid */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">Modules</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {modules.map(({ icon: Icon, label, href, phase, color }) => (
            <a key={href} href={href}>
              <Card className="hover:border-primary/50 hover:shadow-sm transition-all cursor-pointer h-full">
                <CardHeader className="pb-2">
                  <Icon className={`h-6 w-6 ${color}`} />
                </CardHeader>
                <CardContent className="space-y-1">
                  <CardTitle className="text-base">{label}</CardTitle>
                  <Badge variant="secondary" className="text-xs">{phase}</Badge>
                </CardContent>
              </Card>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
