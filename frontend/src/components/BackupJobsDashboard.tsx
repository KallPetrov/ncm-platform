import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Play, 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Calendar,
  Server
} from "lucide-react"
import { api } from "@/lib/api"

interface BackupJob {
  id: number
  device_id: number
  device_name: string
  status: string
  scheduled_time: string
  completed_time: string | null
  error_message: string | null
}

export function BackupJobsDashboard() {
  const [backupJobs, setBackupJobs] = React.useState<BackupJob[]>([])
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    loadBackupJobs()
  }, [])

  const loadBackupJobs = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getBackupJobs()
      setBackupJobs(data)
    } catch (err) {
      setError("Failed to load backup jobs")
      console.error("Error loading backup jobs:", err)
    } finally {
      setLoading(false)
    }
  }

  const triggerBackup = async (deviceId: number) => {
    try {
      await api.triggerBackup(deviceId)
      await loadBackupJobs()
    } catch (err) {
      console.error("Error triggering backup:", err)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />
      case "running":
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Completed</Badge>
      case "failed":
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Failed</Badge>
      case "running":
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Running</Badge>
      case "pending":
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">Pending</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const sortedJobs = [...backupJobs].sort((a, b) => 
    new Date(b.scheduled_time).getTime() - new Date(a.scheduled_time).getTime()
  )

  const stats = {
    total: backupJobs.length,
    completed: backupJobs.filter(job => job.status === "completed").length,
    failed: backupJobs.filter(job => job.status === "failed").length,
    running: backupJobs.filter(job => job.status === "running").length,
    pending: backupJobs.filter(job => job.status === "pending").length,
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running</CardTitle>
            <RefreshCw className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.running}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          </CardContent>
        </Card>
      </div>

      {/* Backup Jobs List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Backup Jobs</CardTitle>
              <CardDescription>
                Monitor and manage backup operations
              </CardDescription>
            </div>
            <Button onClick={loadBackupJobs} disabled={loading} variant="outline" size="sm">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading backup jobs...</div>
          ) : error ? (
            <div className="text-center py-8 text-destructive">{error}</div>
          ) : sortedJobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No backup jobs found
            </div>
          ) : (
            <ScrollArea className="h-[500px] w-full">
              <div className="space-y-3">
                {sortedJobs.map((job) => (
                  <div
                    key={job.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(job.status)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{job.device_name}</span>
                          {getStatusBadge(job.status)}
                        </div>
                        <div className="text-sm text-muted-foreground flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Scheduled: {new Date(job.scheduled_time).toLocaleString()}
                          </span>
                          {job.completed_time && (
                            <span className="flex items-center gap-1">
                              <CheckCircle className="h-3 w-3" />
                              Completed: {new Date(job.completed_time).toLocaleString()}
                            </span>
                          )}
                        </div>
                        {job.error_message && (
                          <div className="text-sm text-red-500 mt-1">
                            Error: {job.error_message}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {job.status === "pending" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => triggerBackup(job.device_id)}
                        >
                          <Play className="h-4 w-4 mr-1" />
                          Run Now
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
