import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, ArrowLeft } from "lucide-react"
import { api } from "@/lib/api"

interface LoginFormProps {
  onLoginSuccess: () => void
}

type FormMode = "login" | "register" | "reset"

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [mode, setMode] = React.useState<FormMode>("login")

  // Input fields
  const [username, setUsername] = React.useState("")
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [confirmPassword, setConfirmPassword] = React.useState("")

  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [success, setSuccess] = React.useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (mode === "login") {
        await api.login(username, password)
        onLoginSuccess()
      } else if (mode === "register") {
        if (password !== confirmPassword) {
          throw new Error("Passwords do not match")
        }
        await api.register(username, email, password)
        setSuccess("Account registered successfully! You can now log in.")
        setMode("login")
        // Clear passwords
        setPassword("")
        setConfirmPassword("")
      } else if (mode === "reset") {
        if (password !== confirmPassword) {
          throw new Error("Passwords do not match")
        }
        await api.resetPassword(username, email, password)
        setSuccess("Password reset successful! You can now log in with your new password.")
        setMode("login")
        // Clear passwords
        setPassword("")
        setConfirmPassword("")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred. Please try again.")
      console.error(`${mode} error:`, err)
    } finally {
      setLoading(false)
    }
  }

  const switchMode = (newMode: FormMode) => {
    setMode(newMode)
    setError(null)
    setSuccess(null)
    // Clear credentials
    setPassword("")
    setConfirmPassword("")
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">NCM Platform</CardTitle>
            {mode !== "login" && (
              <Button
                variant="ghost"
                size="sm"
                className="flex items-center gap-1"
                onClick={() => switchMode("login")}
                disabled={loading}
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
            )}
          </div>
          <CardDescription>
            {mode === "login" && "Enter your credentials to access the platform"}
            {mode === "register" && "Create a new administrator account"}
            {mode === "reset" && "Verify your username and email to reset password"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {success && (
            <div className="mb-4 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            {mode === "register" || mode === "reset" ? (
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            ) : null}

            <div className="space-y-2">
              <Label htmlFor="password">
                {mode === "reset" ? "New Password" : "Password"}
              </Label>
              <Input
                id="password"
                type="password"
                placeholder={mode === "reset" ? "Enter your new password" : "Enter your password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            {mode === "register" || mode === "reset" ? (
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            ) : null}

            {error && (
              <div className="text-sm text-red-500">{error}</div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {mode === "login" && "Signing in..."}
                  {mode === "register" && "Creating account..."}
                  {mode === "reset" && "Resetting password..."}
                </>
              ) : (
                <>
                  {mode === "login" && "Sign In"}
                  {mode === "register" && "Register Account"}
                  {mode === "reset" && "Reset Password"}
                </>
              )}
            </Button>
          </form>

          {mode === "login" && (
            <div className="mt-4 flex flex-col gap-2 text-center text-sm">
              <button
                type="button"
                className="text-primary hover:underline"
                onClick={() => switchMode("reset")}
              >
                Forgot Password?
              </button>
              <div className="text-muted-foreground">
                Don't have an account?{" "}
                <button
                  type="button"
                  className="text-primary hover:underline"
                  onClick={() => switchMode("register")}
                >
                  Register here
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
