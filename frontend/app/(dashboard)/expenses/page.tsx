import { CreditCard } from "lucide-react"
import { ComingSoon } from "@/components/ui/coming-soon"

export default function ExpensesPage() {
  return (
    <ComingSoon
      icon={CreditCard}
      title="Expenses"
      phase="Phase 4"
      description="Track your spending, categorize transactions, and stay on top of your monthly budget."
      features={[
        "Add expenses with category and amount",
        "Monthly spending totals",
        "Category breakdown chart",
        "CSV export",
      ]}
    />
  )
}
