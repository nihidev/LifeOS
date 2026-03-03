import { Brain } from "lucide-react"
import { ComingSoon } from "@/components/ui/coming-soon"

export default function SelfAssessmentPage() {
  return (
    <ComingSoon
      icon={Brain}
      title="Self Assessment"
      phase="Phase 3"
      description="Score yourself daily across key life dimensions — discipline, focus, health, and mindset."
      features={[
        "Daily 1–10 score per dimension",
        "Weekly average trend lines",
        "Reflection notes per entry",
        "Monthly report view",
      ]}
    />
  )
}
