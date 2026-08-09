import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { GitCompare, FileText, Clock } from "lucide-react"
import { api } from "@/lib/api"

interface Configuration {
  id: number
  device_id: number
  version: number
  content: string
  created_at: string
}

interface ConfigurationViewerProps {
  deviceId: number
  deviceName: string
}

export function ConfigurationViewer({ deviceId, deviceName }: ConfigurationViewerProps) {
  const [configurations, setConfigurations] = React.useState<Configuration[]>([])
  const [selectedVersionA, setSelectedVersionA] = React.useState<number | null>(null)
  const [selectedVersionB, setSelectedVersionB] = React.useState<number | null>(null)
  const [diff, setDiff] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    loadConfigurations()
  }, [deviceId])

  const loadConfigurations = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getDeviceConfigurations(deviceId)
      setConfigurations(data)
      if (data.length > 0) {
        setSelectedVersionA(data[0].version)
        setSelectedVersionB(data.length > 1 ? data[1].version : data[0].version)
      }
    } catch (err) {
      setError("Failed to load configurations")
      console.error("Error loading configurations:", err)
    } finally {
      setLoading(false)
    }
  }

  const loadDiff = async () => {
    if (selectedVersionA === null || selectedVersionB === null) return
    
    setLoading(true)
    setError(null)
    try {
      const data = await api.getConfigurationDiff(deviceId, selectedVersionA, selectedVersionB)
      setDiff(data.diff || "No differences found")
    } catch (err) {
      setError("Failed to load diff")
      console.error("Error loading diff:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleVersionAChange = (value: string) => {
    setSelectedVersionA(parseInt(value))
  }

  const handleVersionBChange = (value: string) => {
    setSelectedVersionB(parseInt(value))
  }

  const handleCompare = () => {
    loadDiff()
  }

  const sortedConfigs = [...configurations].sort((a, b) => b.version - a.version)

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Configuration Viewer - {deviceName}
          </CardTitle>
          <CardDescription>
            View and compare configuration versions for this device
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Version A</label>
                <Select value={selectedVersionA?.toString()} onValueChange={handleVersionAChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select version A" />
                  </SelectTrigger>
                  <SelectContent>
                    {sortedConfigs.map((config) => (
                      <SelectItem key={config.version} value={config.version.toString()}>
                        Version {config.version} - {new Date(config.created_at).toLocaleString()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center pt-6">
                <GitCompare className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Version B</label>
                <Select value={selectedVersionB?.toString()} onValueChange={handleVersionBChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select version B" />
                  </SelectTrigger>
                  <SelectContent>
                    {sortedConfigs.map((config) => (
                      <SelectItem key={config.version} value={config.version.toString()}>
                        Version {config.version} - {new Date(config.created_at).toLocaleString()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-end">
                <Button onClick={handleCompare} disabled={!selectedVersionA || !selectedVersionB || loading}>
                  {loading ? "Loading..." : "Compare"}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="diff" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="diff">Diff View</TabsTrigger>
          <TabsTrigger value="history">Version History</TabsTrigger>
        </TabsList>
        
        <TabsContent value="diff" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Configuration Diff</CardTitle>
              <CardDescription>
                Differences between Version {selectedVersionA} and Version {selectedVersionB}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-muted-foreground">Loading diff...</div>
              ) : error ? (
                <div className="text-center py-8 text-destructive">{error}</div>
              ) : diff ? (
                <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                  <pre className="text-sm whitespace-pre-wrap font-mono">{diff}</pre>
                </ScrollArea>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Select two versions and click Compare to see differences
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Version History</CardTitle>
              <CardDescription>
                All configuration versions for {deviceName}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-muted-foreground">Loading configurations...</div>
              ) : error ? (
                <div className="text-center py-8 text-destructive">{error}</div>
              ) : sortedConfigs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No configurations found for this device
                </div>
              ) : (
                <ScrollArea className="h-[400px] w-full">
                  <div className="space-y-2">
                    {sortedConfigs.map((config) => (
                      <div
                        key={config.version}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent cursor-pointer"
                        onClick={() => setSelectedVersionA(config.version)}
                      >
                        <div className="flex items-center gap-3">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <div className="font-medium">Version {config.version}</div>
                            <div className="text-sm text-muted-foreground">
                              {new Date(config.created_at).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">
                          View
                        </Button>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
