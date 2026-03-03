import { Calendar } from "lucide-react"
import { ComingSoon } from "@/components/ui/coming-soon"

export default function AppointmentsPage() {
  return (
    <ComingSoon
      icon={Calendar}
      title="Appointments"
      phase="Phase 8"
      description="Keep track of upcoming appointments, deadlines, and important events in one place."
      features={[
        "Add appointments with date and time",
        "Location and notes fields",
        "Upcoming appointments list",
        "Email reminders",
      ]}
    />
  )
}
