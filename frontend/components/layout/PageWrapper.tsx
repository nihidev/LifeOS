interface PageWrapperProps {
  title: string
  children: React.ReactNode
}

export function PageWrapper({ children }: PageWrapperProps) {
  return <div className="p-8">{children}</div>
}
