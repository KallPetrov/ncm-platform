import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
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
  const [saved, setSaved] = React.useState(false)
  
  // Database settings
  const [dbUrl, setDbUrl] = React.useState("postgresql://ncm_user:ncm_password@localhost:5432/ncm_db")
  const [redisUrl, setRedisUrl] = React.useState("redis://localhost:6379/0")
  
  // Notification settings
  const [enableEmail, setEnableEmail] = React.useState(false)
  const [emailSmtp, setEmailSmtp] = React.useState("")
  const [emailPort, setEmailPort] = React.useState("587")
  
  // Security settings
  const [sessionTimeout, setSessionTimeout] = React.useState("30")
  const [maxLoginAttempts, setMaxLoginAttempts] = React.useState("5")
  
  // Network settings
  const [apiTimeout, setApiTimeout] = React.useState("30")
  const [maxConcurrentBackups, setMaxConcurrentBackups] = React.useState("10")

  const handleSave = async () => {
    setLoading(true)
    setSaved(false)
    
    // Simulate API call to save settings
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setSaved(true)
    setLoading(false)
    
    setTimeout(() => setSaved(false), 3000)
  }

  const handleTestConnection = async (type: string) => {
    setLoading(true)
    
    // Simulate connection test
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setLoading(false)
    alert(`${type} connection test successful!`)
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
          Settings saved successfully!
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
                  onClick={() => handleTestConnection("PostgreSQL")}
                  disabled={loading}
                >
                  Test PostgreSQL
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => handleTestConnection("Redis")}
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
