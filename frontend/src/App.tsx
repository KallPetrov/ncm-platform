import * as React from "react"
import { DeviceManagement } from "./components/DeviceManagement"
import { LoginForm } from "./components/LoginForm"
import { ConfigurationViewer } from "./components/ConfigurationViewer"
import { BackupJobsDashboard } from "./components/BackupJobsDashboard"
import { SettingsPanel } from "./components/SettingsPanel"
import { DashboardOverview } from "./components/DashboardOverview"
import { ComplianceReports } from "./components/ComplianceReports"
import { AutomationPanel } from "./components/AutomationPanel"
import { AuditLogsPanel } from "./components/AuditLogsPanel"
import { AIAssistantPanel } from "./components/AIAssistantPanel"
import { Button } from "./components/ui/button"
import { Settings, Server, FileText, Activity, Menu, LogOut, LayoutDashboard, ShieldCheck, Zap, History, Sparkles } from "lucide-react"
import { api } from "./lib/api"

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false)
  const [activeTab, setActiveTab] = React.useState("devices")
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

  // Check if user is already logged in on mount
  React.useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      setIsAuthenticated(true)
    }
  }, [])

  const handleLoginSuccess = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    api.logout()
    setIsAuthenticated(false)
  }

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />
  }

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "devices", label: "Devices", icon: Server },
    { id: "configurations", label: "Configurations", icon: FileText },
    { id: "compliance", label: "Compliance", icon: ShieldCheck },
    { id: "automation", label: "Automation", icon: Zap },
    { id: "ai-assistant", label: "AI Асистент", icon: Sparkles },
    { id: "backups", label: "Backup Jobs", icon: Activity },
    { id: "audit", label: "Audit Logs", icon: History },
    { id: "settings", label: "Settings", icon: Settings },
  ]

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-16"
        } border-r bg-card transition-all duration-300`}
      >
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center justify-between border-b px-4">
            {sidebarOpen && (
              <h1 className="text-xl font-bold">LANi-Platform</h1>
            )}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <Menu className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <nav className="flex-1 space-y-2 p-4">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {sidebarOpen && <span>{tab.label}</span>}
                </button>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto p-6">
          {activeTab === "dashboard" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
              <p className="text-muted-foreground">
                Monitor platform health, device state, and recent backup activity.
              </p>
              <DashboardOverview />
            </div>
          )}
          {activeTab === "devices" && <DeviceManagement />}
          {activeTab === "configurations" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">Configurations</h2>
              <p className="text-muted-foreground">
                View and manage device configuration history
              </p>
              <ConfigurationViewer />
            </div>
          )}
          {activeTab === "compliance" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">Compliance Reports</h2>
              <p className="text-muted-foreground">
                Review per-device compliance results and rule status.
              </p>
              <ComplianceReports />
            </div>
          )}
          {activeTab === "automation" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">Automation</h2>
              <p className="text-muted-foreground">
                Validate and apply configuration templates across your devices.
              </p>
              <AutomationPanel />
            </div>
          )}
          {activeTab === "ai-assistant" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">AI Асистент</h2>
              <p className="text-muted-foreground">
                Интелигентен асистент за мрежови анализи, одит и генериране на конфигурации на български език.
              </p>
              <AIAssistantPanel />
            </div>
          )}
          {activeTab === "backups" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">Backup Jobs</h2>
              <p className="text-muted-foreground">
                Monitor and manage backup operations
              </p>
              <BackupJobsDashboard />
            </div>
          )}
          {activeTab === "audit" && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tight">Audit Logs</h2>
              <p className="text-muted-foreground">
                Review recent administrative actions and platform changes.
              </p>
              <AuditLogsPanel />
            </div>
          )}
          {activeTab === "settings" && <SettingsPanel />}
        </div>
      </main>
    </div>
  )
}

export default App
