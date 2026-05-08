export function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="p-4 pb-24 md:p-8 md:pb-8">
      {children}
    </div>
  )
}
