import { LucideIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface ComingSoonProps {
  icon: LucideIcon
  title: string
  description: string
  phase: string
  features: string[]
}

export function ComingSoon({ icon: Icon, title, description, phase, features }: ComingSoonProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center gap-6">
      <div className="rounded-full bg-muted p-6">
        <Icon className="h-12 w-12 text-muted-foreground" />
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-center gap-2">
          <h1 className="text-2xl font-bold">{title}</h1>
          <Badge variant="secondary">{phase}</Badge>
        </div>
        <p className="text-muted-foreground max-w-md">{description}</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
        {features.map((f) => (
          <div key={f} className="flex items-center gap-2 rounded-lg border bg-card p-3 text-sm text-left">
            <div className="h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
            {f}
          </div>
        ))}
      </div>
    </div>
  )
}
