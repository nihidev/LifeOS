import React from "react"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import LoginPage from "@/app/(auth)/login/page"
import * as auth from "@/lib/auth"

// Mock the auth module
jest.mock("@/lib/auth", () => ({
  signInWithMagicLink: jest.fn(),
}))

// Mock shadcn components that depend on Radix UI internals
jest.mock("@/components/ui/card", () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardContent: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  CardHeader: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  CardTitle: ({ children }: { children: React.ReactNode }) => (
    <h1>{children}</h1>
  ),
  CardDescription: ({ children }: { children: React.ReactNode }) => (
    <p>{children}</p>
  ),
}))

jest.mock("@/components/ui/button", () => ({
  Button: ({
    children,
    onClick,
    type,
    disabled,
    ...rest
  }: React.ButtonHTMLAttributes<HTMLButtonElement>) => (
    <button type={type} onClick={onClick} disabled={disabled} {...rest}>
      {children}
    </button>
  ),
}))

jest.mock("@/components/ui/input", () => ({
  Input: (props: React.InputHTMLAttributes<HTMLInputElement>) => (
    <input {...props} />
  ),
}))

jest.mock("@/components/ui/label", () => ({
  Label: ({
    children,
    ...props
  }: React.LabelHTMLAttributes<HTMLLabelElement>) => (
    <label {...props}>{children}</label>
  ),
}))

describe("LoginPage", () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it("renders the email input and submit button", () => {
    render(<LoginPage />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(
      screen.getByRole("button", { name: /send magic link/i })
    ).toBeInTheDocument()
  })

  it("shows loading state while submitting", async () => {
    const mockSignIn = jest.mocked(auth.signInWithMagicLink)
    mockSignIn.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 200))
    )

    render(<LoginPage />)
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "test@example.com" },
    })
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }))

    expect(screen.getByRole("button", { name: /sending/i })).toBeDisabled()
  })

  it("shows success message after sending", async () => {
    const mockSignIn = jest.mocked(auth.signInWithMagicLink)
    mockSignIn.mockResolvedValueOnce(undefined)

    render(<LoginPage />)
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "user@example.com" },
    })
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }))

    await waitFor(() => {
      expect(screen.getByText(/magic link sent/i)).toBeInTheDocument()
      expect(screen.getByText("user@example.com")).toBeInTheDocument()
    })
  })

  it("shows error message on failure", async () => {
    const mockSignIn = jest.mocked(auth.signInWithMagicLink)
    mockSignIn.mockRejectedValueOnce(new Error("Rate limit exceeded"))

    render(<LoginPage />)
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "bad@example.com" },
    })
    fireEvent.click(screen.getByRole("button", { name: /send magic link/i }))

    await waitFor(() => {
      expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument()
    })
  })

  it("calls signInWithMagicLink with the entered email", async () => {
    const mockSignIn = jest.mocked(auth.signInWithMagicLink)
    mockSignIn.mockResolvedValueOnce(undefined)

    render(<LoginPage />)
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "hello@lifeos.app" },
    })
    fireEvent.submit(screen.getByRole("button", { name: /send magic link/i }).closest("form")!)

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith("hello@lifeos.app")
    })
  })
})
