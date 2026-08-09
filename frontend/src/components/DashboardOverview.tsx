import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Server, FileText, CheckCircle2, ShieldCheck } from "lucide-react"
import { api } from "@/lib/api"

interface DashboardSummary {
  total_devices: number
  online_devices: number
  offline_devices: number
  total_configurations: number
  successful_backup_jobs: number
  pending_backup_jobs: number
  latest_configuration_version: number | null
  compliance_summary: {
    overall_status: string
    compliance_percentage: number
    total_rules: number
    compliant_rules: number
    non_compliant_rules: number
  }
}

export function DashboardOverview() {
  const [summary, setSummary] = React.useState<DashboardSummary | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    loadSummary()
  }, [])

  const loadSummary = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getDashboardOverview()
      setSummary(data)
    } catch (err) {
      setError("Failed to load dashboard summary")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-sm text-muted-foreground">Loading dashboard...</div>
  }

  if (error || !summary) {
    return <div className="text-sm text-destructive">{error || "No dashboard data available"}</div>
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Devices</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_devices}</div>
            <p className="text-xs text-muted-foreground">{summary.online_devices} online / {summary.offline_devices} offline</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Configurations</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_configurations}</div>
            <p className="text-xs text-muted-foreground">Latest version: {summary.latest_configuration_version ?? "n/a"}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Backup Jobs</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.successful_backup_jobs}</div>
            <p className="text-xs text-muted-foreground">{summary.pending_backup_jobs} pending</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance</CardTitle>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{summary.compliance_summary.overall_status}</div>
            <p className="text-xs text-muted-foreground">{summary.compliance_summary.compliance_percentage}% coverage</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Operational health
          </CardTitle>
          <CardDescription>
            Summary of the current platform state from the backend services.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <div className="flex items-center justify-between rounded-lg border p-3">
            <span>Online devices</span>
            <span className="font-medium text-foreground">{summary.online_devices}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <span>Pending backup jobs</span>
            <span className="font-medium text-foreground">{summary.pending_backup_jobs}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <span>Compliant rules</span>
            <span className="font-medium text-foreground">{summary.compliance_summary.compliant_rules}/{summary.compliance_summary.total_rules}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
