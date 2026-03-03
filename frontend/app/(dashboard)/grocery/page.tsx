import { ShoppingCart } from "lucide-react"
import { ComingSoon } from "@/components/ui/coming-soon"

export default function GroceryPage() {
  return (
    <ComingSoon
      icon={ShoppingCart}
      title="Grocery List"
      phase="Phase 8"
      description="Manage your weekly grocery list, check off items as you shop, and reuse past lists."
      features={[
        "Add items with quantities",
        "Check off as you shop",
        "Organise by store section",
        "Reuse previous lists",
      ]}
    />
  )
}
