import * as React from "react"
import { api } from "../lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { RefreshCw, History, UserCircle2, Filter } from "lucide-react"

interface AuditLogItem {
  id: number
  username?: string | null
  action: string
  resource_type?: string | null
  resource_id?: number | null
  details?: string | null
  role?: string | null
  created_at?: string
}

export function AuditLogsPanel() {
  const [logs, setLogs] = React.useState<AuditLogItem[]>([])
  const [loading, setLoading] = React.useState(true)
  const [refreshing, setRefreshing] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [actionFilter, setActionFilter] = React.useState("")
  const [usernameFilter, setUsernameFilter] = React.useState("")

  const loadLogs = React.useCallback(async () => {
    try {
      setError(null)
      const data = await api.getAuditLogs(100, actionFilter || undefined, usernameFilter || undefined)
      setLogs(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit logs")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [actionFilter, usernameFilter])

  React.useEffect(() => {
    void loadLogs()
  }, [loadLogs])

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadLogs()
  }

  if (loading) {
    return <div className="text-sm text-muted-foreground">Loading audit logs...</div>
  }

  if (error) {
    return <div className="text-sm text-red-600">{error}</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Audit Logs</h2>
          <p className="text-sm text-muted-foreground">
            Review recent administrative actions and platform activity.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-md border px-3 py-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <input
              value={actionFilter}
              onChange={(event) => setActionFilter(event.target.value)}
              placeholder="Action"
              className="bg-transparent text-sm outline-none"
            />
          </div>
          <div className="flex items-center gap-2 rounded-md border px-3 py-2">
            <UserCircle2 className="h-4 w-4 text-muted-foreground" />
            <input
              value={usernameFilter}
              onChange={(event) => setUsernameFilter(event.target.value)}
              placeholder="Username"
              className="bg-transparent text-sm outline-none"
            />
          </div>
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>

      {logs.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">No audit activity has been recorded yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <Card key={log.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <CardTitle className="text-base">{log.action}</CardTitle>
                    <CardDescription>
                      {log.resource_type ? `${log.resource_type}` : "Platform"}
                      {log.resource_id ? ` #${log.resource_id}` : ""}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary">{log.role || "system"}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <UserCircle2 className="h-4 w-4" />
                  <span>{log.username || "system"}</span>
                  <span>•</span>
                  <span className="capitalize">{log.role || "unknown"}</span>
                  <span>•</span>
                  <span>{log.created_at ? new Date(log.created_at).toLocaleString() : "Unknown time"}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <History className="h-4 w-4" />
                  <span>{log.details || "No additional details were recorded."}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
