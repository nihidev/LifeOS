import { cn, formatDate, formatCurrency, getToday } from "@/lib/utils"

describe("cn()", () => {
  it("merges class names", () => {
    expect(cn("a", "b")).toBe("a b")
  })

  it("deduplicates conflicting Tailwind classes (last wins)", () => {
    expect(cn("p-2", "p-4")).toBe("p-4")
  })

  it("handles conditional classes", () => {
    const isActive = true
    expect(cn("base", isActive && "active")).toBe("base active")
  })

  it("filters falsy values", () => {
    expect(cn("base", false, undefined, null, "end")).toBe("base end")
  })
})

describe("formatDate()", () => {
  it("formats a Date object to default MMM d, yyyy", () => {
    const result = formatDate(new Date("2025-06-15"))
    expect(result).toBe("Jun 15, 2025")
  })

  it("formats a date string", () => {
    expect(formatDate("2025-01-01")).toBe("Jan 1, 2025")
  })

  it("accepts a custom format string", () => {
    expect(formatDate("2025-12-25", "dd/MM/yyyy")).toBe("25/12/2025")
  })
})

describe("formatCurrency()", () => {
  it("formats USD by default", () => {
    expect(formatCurrency(1234.56)).toBe("$1,234.56")
  })

  it("formats zero", () => {
    expect(formatCurrency(0)).toBe("$0.00")
  })

  it("supports other currencies", () => {
    const result = formatCurrency(100, "EUR")
    expect(result).toContain("100")
  })
})

describe("getToday()", () => {
  it("returns a YYYY-MM-DD string", () => {
    const today = getToday()
    expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it("matches today's date", () => {
    const expected = new Date().toISOString().split("T")[0]
    expect(getToday()).toBe(expected)
  })
})
