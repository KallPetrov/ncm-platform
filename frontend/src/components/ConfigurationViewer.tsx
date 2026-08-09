import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { GitCompare, FileText, Clock, Download } from "lucide-react"
import { api, type Device } from "@/lib/api"

interface Configuration {
  id: number
  device_id: number
  version: number
  content: string
  created_at: string
}

interface ConfigurationViewerProps {
  deviceId?: number
}

export function ConfigurationViewer({ deviceId: propDeviceId }: ConfigurationViewerProps) {
  const [devices, setDevices] = React.useState<Device[]>([])
  const [selectedDeviceId, setSelectedDeviceId] = React.useState<number | null>(null)
  const [selectedDevice, setSelectedDevice] = React.useState<Device | null>(null)

  const [configurations, setConfigurations] = React.useState<Configuration[]>([])
  const [selectedVersionA, setSelectedVersionA] = React.useState<number | null>(null)
  const [selectedVersionB, setSelectedVersionB] = React.useState<number | null>(null)
  const [diff, setDiff] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  // Load all devices on mount
  React.useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    try {
      setLoading(true)
      const list = await api.getDevices()
      setDevices(list)

      if (propDeviceId) {
        setSelectedDeviceId(propDeviceId)
        const d = list.find(item => item.id === propDeviceId)
        setSelectedDevice(d || null)
      } else if (list.length > 0) {
        setSelectedDeviceId(list[0].id)
        setSelectedDevice(list[0])
      }
    } catch (err) {
      setError("Failed to load devices")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Reload configurations when selected device changes
  React.useEffect(() => {
    if (selectedDeviceId !== null) {
      void loadConfigurations(selectedDeviceId)
    }
  }, [selectedDeviceId])

  const loadConfigurations = async (id: number) => {
    setLoading(true)
    setError(null)
    setDiff(null)
    try {
      const data = await api.getDeviceConfigurations(id)
      setConfigurations(data)
      if (data.length > 0) {
        setSelectedVersionA(data[0].version)
        setSelectedVersionB(data.length > 1 ? data[1].version : data[0].version)
      } else {
        setSelectedVersionA(null)
        setSelectedVersionB(null)
      }
    } catch (err) {
      setError("Failed to load configurations")
      console.error("Error loading configurations:", err)
    } finally {
      setLoading(false)
    }
  }

  const loadDiff = async () => {
    if (selectedDeviceId === null || selectedVersionA === null || selectedVersionB === null) return
    
    setLoading(true)
    setError(null)
    try {
      const data = await api.getConfigurationDiff(selectedDeviceId, selectedVersionA, selectedVersionB)
      setDiff(data.diff || "No differences found")
    } catch (err) {
      setError("Failed to load diff")
      console.error("Error loading diff:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeviceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const id = parseInt(event.target.value)
    setSelectedDeviceId(id)
    const d = devices.find(item => item.id === id)
    setSelectedDevice(d || null)
  }

  const handleCompare = () => {
    loadDiff()
  }

  const handleDownload = async (version: number) => {
    if (selectedDeviceId === null) return
    try {
      const data = await api.getConfigurationByVersion(selectedDeviceId, version)
      const content = data.content || ""
      const blob = new Blob([content], { type: "text/plain;charset=utf-8" })
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.setAttribute("download", `config_${selectedDevice?.name || "device"}_v${version}.txt`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      alert("Failed to download configuration version.")
      console.error(err)
    }
  }

  const sortedConfigs = [...configurations].sort((a, b) => b.version - a.version)

  return (
    <div className="space-y-6">
      {/* Device Selector */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle>Select Device</CardTitle>
          <CardDescription>
            Choose a registered device to view or compare configuration snapshots
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              value={selectedDeviceId || ""}
              onChange={handleDeviceChange}
              disabled={devices.length === 0}
            >
              {devices.length === 0 && <option>No devices found</option>}
              {devices.map((device) => (
                <option key={device.id} value={device.id}>
                  {device.name} ({device.ip_address}) - {device.vendor}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {selectedDevice && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Configuration Viewer - {selectedDevice.name}
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
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none"
                      value={selectedVersionA || ""}
                      onChange={(e) => setSelectedVersionA(parseInt(e.target.value))}
                      disabled={sortedConfigs.length === 0}
                    >
                      {sortedConfigs.map((config) => (
                        <option key={config.version} value={config.version}>
                          Version {config.version} - {new Date(config.created_at).toLocaleString()}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center pt-6">
                    <GitCompare className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div className="flex-1">
                    <label className="text-sm font-medium mb-2 block">Version B</label>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none"
                      value={selectedVersionB || ""}
                      onChange={(e) => setSelectedVersionB(parseInt(e.target.value))}
                      disabled={sortedConfigs.length === 0}
                    >
                      {sortedConfigs.map((config) => (
                        <option key={config.version} value={config.version}>
                          Version {config.version} - {new Date(config.created_at).toLocaleString()}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-end pt-6">
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
                    All configuration versions for {selectedDevice.name}
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
                          >
                            <div className="flex items-center gap-3" onClick={() => setSelectedVersionA(config.version)}>
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <div>
                                <div className="font-medium">Version {config.version}</div>
                                <div className="text-sm text-muted-foreground">
                                  {new Date(config.created_at).toLocaleString()}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button variant="outline" size="sm" onClick={() => handleDownload(config.version)}>
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </Button>
                              <Button variant="ghost" size="sm" onClick={() => setSelectedVersionA(config.version)}>
                                View
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  )
}
