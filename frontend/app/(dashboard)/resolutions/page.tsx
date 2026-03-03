import { Target } from "lucide-react"
import { ComingSoon } from "@/components/ui/coming-soon"

export default function ResolutionsPage() {
  return (
    <ComingSoon
      icon={Target}
      title="Resolutions"
      phase="Phase 5"
      description="Set annual goals, break them into milestones, and track your progress throughout the year."
      features={[
        "Create resolutions with target dates",
        "Milestone check-ins",
        "Progress percentage tracker",
        "Year-in-review summary",
      ]}
    />
  )
}
