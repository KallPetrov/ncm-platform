import * as React from "react"
import { api } from "../lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { AlertTriangle, CheckCircle2, RefreshCw, ShieldCheck } from "lucide-react"

interface ComplianceReportItem {
  device_id: number
  device_name: string
  compliance_percentage: number
  overall_status: string
  total_rules: number
  compliant_rules: number
  non_compliant_rules: number
  results: Array<{
    rule_name: string
    severity: string
    status: string
    details: string
    message?: string
  }>
}

export function ComplianceReports() {
  const [reports, setReports] = React.useState<ComplianceReportItem[]>([])
  const [loading, setLoading] = React.useState(true)
  const [refreshing, setRefreshing] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const loadReports = React.useCallback(async () => {
    try {
      setError(null)
      const devices = await api.getDevices(0, 50)
      const reportsData = await Promise.all(
        devices.map(async (device) => {
          try {
            const report = await api.getDeviceCompliance(device.id)
            return {
              ...report,
              device_name: device.name,
              device_id: device.id,
            }
          } catch {
            return null
          }
        })
      )

      setReports(reportsData.filter(Boolean) as ComplianceReportItem[])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load compliance reports")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  React.useEffect(() => {
    void loadReports()
  }, [loadReports])

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadReports()
  }

  const compliantDevices = reports.filter((report) => report.overall_status === "compliant").length
  const nonCompliantDevices = reports.length - compliantDevices

  if (loading) {
    return <div className="text-sm text-muted-foreground">Loading compliance reports...</div>
  }

  if (error) {
    return <div className="text-sm text-red-600">{error}</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-muted-foreground">
            {reports.length} device report{reports.length === 1 ? "" : "s"} loaded
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
          {refreshing ? "Refreshing..." : "Refresh"}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Compliant devices</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <span className="text-2xl font-semibold">{compliantDevices}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Needs attention</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <span className="text-2xl font-semibold">{nonCompliantDevices}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Coverage</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-blue-600" />
            <span className="text-2xl font-semibold">{reports.length}</span>
          </CardContent>
        </Card>
      </div>

      {reports.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">No compliance data is available yet.</p>
          </CardContent>
        </Card>
      ) : (
        reports.map((report) => (
          <Card key={report.device_id}>
            <CardHeader>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <CardTitle>{report.device_name}</CardTitle>
                  <CardDescription>
                    {report.compliant_rules}/{report.total_rules} rules passing
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={report.overall_status === "compliant" ? "default" : "secondary"}>
                    {report.overall_status}
                  </Badge>
                  <span className="text-sm font-medium">{report.compliance_percentage}%</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {report.results.map((result) => (
                <div key={`${report.device_id}-${result.rule_name}`} className="rounded-lg border p-3">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-medium">{result.rule_name}</span>
                    <Badge variant={result.status === "compliant" ? "default" : "destructive"}>
                      {result.status}
                    </Badge>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{result.message || result.details}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        ))
      )}
    </div>
  )
}
