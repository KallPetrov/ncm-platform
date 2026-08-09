import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { api } from "@/lib/api"
import { 
  Database, 
  Bell, 
  Shield, 
  Network,
  Save,
  RefreshCw
} from "lucide-react"

export function SettingsPanel() {
  const [loading, setLoading] = React.useState(false)
  const [fetching, setFetching] = React.useState(true)
  const [saved, setSaved] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  
  // Database settings
  const [dbUrl, setDbUrl] = React.useState("")
  const [redisUrl, setRedisUrl] = React.useState("")
  
  // Notification settings
  const [enableEmail, setEnableEmail] = React.useState(false)
  const [emailSmtp, setEmailSmtp] = React.useState("")
  const [emailPort, setEmailPort] = React.useState("")
  
  // Security settings
  const [sessionTimeout, setSessionTimeout] = React.useState("")
  const [maxLoginAttempts, setMaxLoginAttempts] = React.useState("")
  
  // Network settings
  const [apiTimeout, setApiTimeout] = React.useState("")
  const [maxConcurrentBackups, setMaxConcurrentBackups] = React.useState("")

  React.useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setFetching(true)
      setError(null)
      const data = await api.getSettings()

      setDbUrl(data.db_url || "")
      setRedisUrl(data.redis_url || "")
      setEnableEmail(data.enable_email ?? false)
      setEmailSmtp(data.email_smtp || "")
      setEmailPort(data.email_port || "")
      setSessionTimeout(data.session_timeout || "30")
      setMaxLoginAttempts(data.max_login_attempts || "5")
      setApiTimeout(data.api_timeout || "30")
      setMaxConcurrentBackups(data.max_concurrent_backups || "10")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load platform settings")
    } finally {
      setFetching(false)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    setSaved(false)
    setError(null)
    
    try {
      await api.updateSettings({
        db_url: dbUrl,
        redis_url: redisUrl,
        enable_email: enableEmail,
        email_smtp: emailSmtp,
        email_port: emailPort,
        session_timeout: sessionTimeout,
        max_login_attempts: maxLoginAttempts,
        api_timeout: apiTimeout,
        max_concurrent_backups: maxConcurrentBackups
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings")
    } finally {
      setLoading(false)
    }
  }

  const handleTestConnection = async (type: string, url: string) => {
    setLoading(true)
    try {
      const response = await api.testSettingsConnection(type.toLowerCase(), url)
      alert(response.message || `${type} connection test successful!`)
    } catch (err) {
      alert(err instanceof Error ? err.message : `${type} connection test failed!`)
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Loading platform settings...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
          <p className="text-muted-foreground">
            Configure platform settings and preferences
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleSave} disabled={loading}>
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Settings
              </>
            )}
          </Button>
        </div>
      </div>

      {saved && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          Platform configurations updated and saved successfully!
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          Error: {error}
        </div>
      )}

      <Tabs defaultValue="database" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
        </TabsList>
        
        <TabsContent value="database" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Database Configuration
              </CardTitle>
              <CardDescription>
                Configure database connections and storage settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="db-url">PostgreSQL Connection URL</Label>
                <Input
                  id="db-url"
                  value={dbUrl}
                  onChange={(e) => setDbUrl(e.target.value)}
                  placeholder="postgresql://user:password@host:port/database"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="redis-url">Redis Connection URL</Label>
                <Input
                  id="redis-url"
                  value={redisUrl}
                  onChange={(e) => setRedisUrl(e.target.value)}
                  placeholder="redis://host:port/database"
                />
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => handleTestConnection("PostgreSQL", dbUrl)}
                  disabled={loading}
                >
                  Test PostgreSQL
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => handleTestConnection("Redis", redisUrl)}
                  disabled={loading}
                >
                  Test Redis
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Settings
              </CardTitle>
              <CardDescription>
                Configure email and push notification preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Enable Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive email alerts for backup failures and system events
                  </p>
                </div>
                <Switch
                  checked={enableEmail}
                  onCheckedChange={setEnableEmail}
                />
              </div>
              
              {enableEmail && (
                <div className="space-y-4 pt-4 border-t">
                  <div className="space-y-2">
                    <Label htmlFor="smtp-server">SMTP Server</Label>
                    <Input
                      id="smtp-server"
                      value={emailSmtp}
                      onChange={(e) => setEmailSmtp(e.target.value)}
                      placeholder="smtp.example.com"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="smtp-port">SMTP Port</Label>
                    <Input
                      id="smtp-port"
                      value={emailPort}
                      onChange={(e) => setEmailPort(e.target.value)}
                      placeholder="587"
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Settings
              </CardTitle>
              <CardDescription>
                Configure authentication and security policies
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="session-timeout">Session Timeout (minutes)</Label>
                <Input
                  id="session-timeout"
                  type="number"
                  value={sessionTimeout}
                  onChange={(e) => setSessionTimeout(e.target.value)}
                  placeholder="30"
                />
                <p className="text-sm text-muted-foreground">
                  User sessions will expire after this period of inactivity
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="max-login">Max Login Attempts</Label>
                <Input
                  id="max-login"
                  type="number"
                  value={maxLoginAttempts}
                  onChange={(e) => setMaxLoginAttempts(e.target.value)}
                  placeholder="5"
                />
                <p className="text-sm text-muted-foreground">
                  Account will be locked after this many failed login attempts
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                Network Settings
              </CardTitle>
              <CardDescription>
                Configure network timeouts and connection limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="api-timeout">API Timeout (seconds)</Label>
                <Input
                  id="api-timeout"
                  type="number"
                  value={apiTimeout}
                  onChange={(e) => setApiTimeout(e.target.value)}
                  placeholder="30"
                />
                <p className="text-sm text-muted-foreground">
                  Maximum time to wait for API responses
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="max-backups">Max Concurrent Backups</Label>
                <Input
                  id="max-backups"
                  type="number"
                  value={maxConcurrentBackups}
                  onChange={(e) => setMaxConcurrentBackups(e.target.value)}
                  placeholder="10"
                />
                <p className="text-sm text-muted-foreground">
                  Maximum number of backup operations running simultaneously
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
