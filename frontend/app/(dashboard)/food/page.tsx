import { UtensilsCrossed } from "lucide-react"
import { ComingSoon } from "@/components/ui/coming-soon"

export default function FoodPage() {
  return (
    <ComingSoon
      icon={UtensilsCrossed}
      title="Food Log"
      phase="Phase 8"
      description="Log your daily meals to stay aware of your nutrition habits and eating patterns."
      features={[
        "Log meals by time of day",
        "Add notes and tags",
        "Daily meal history",
        "Nutrition awareness prompts",
      ]}
    />
  )
}
