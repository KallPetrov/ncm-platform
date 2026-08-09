import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { DeviceDialog } from "@/components/DeviceDialog"
import { Plus, Trash2, RefreshCw, Settings, Loader2 } from "lucide-react"
import { api, type Device } from "@/lib/api"

export function DeviceManagement() {
  const [devices, setDevices] = React.useState<Device[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = React.useState(false)
  const [dialogMode, setDialogMode] = React.useState<"create" | "edit">("create")
  const [selectedDevice, setSelectedDevice] = React.useState<Device | undefined>()

  // Fetch devices on component mount
  React.useEffect(() => {
    fetchDevices()
  }, [])

  const fetchDevices = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getDevices()
      setDevices(data)
    } catch (err) {
      setError("Failed to load devices. Make sure the backend is running.")
      console.error("Error fetching devices:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddDevice = () => {
    setDialogMode("create")
    setSelectedDevice(undefined)
    setDialogOpen(true)
  }

  const handleEditDevice = (device: Device) => {
    setDialogMode("edit")
    setSelectedDevice(device)
    setDialogOpen(true)
  }

  const handleSaveDevice = async (deviceData: any) => {
    try {
      if (dialogMode === "create") {
        const newDevice = await api.createDevice(deviceData)
        setDevices([...devices, newDevice])
      } else if (selectedDevice) {
        const updatedDevice = await api.updateDevice(selectedDevice.id, deviceData)
        setDevices(
          devices.map((d) => (d.id === selectedDevice.id ? updatedDevice : d))
        )
      }
      setDialogOpen(false)
    } catch (err) {
      console.error("Error saving device:", err)
      alert("Failed to save device. Please try again.")
    }
  }

  const handleDeleteDevice = async (deviceId: number) => {
    if (!confirm("Are you sure you want to delete this device?")) {
      return
    }
    
    try {
      await api.deleteDevice(deviceId)
      setDevices(devices.filter((d) => d.id !== deviceId))
    } catch (err) {
      console.error("Error deleting device:", err)
      alert("Failed to delete device. Please try again.")
    }
  }

  const handleBackup = async (deviceId: number) => {
    try {
      await api.triggerBackup(deviceId)
      alert("Backup triggered successfully")
      // Refresh devices to update status
      await fetchDevices()
    } catch (err) {
      console.error("Error triggering backup:", err)
      alert("Failed to trigger backup. Please try again.")
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "text-green-500"
      case "offline":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Device Management</h2>
          <p className="text-muted-foreground">
            Manage your network devices and configurations
          </p>
        </div>
        <Button onClick={handleAddDevice}>
          <Plus className="mr-2 h-4 w-4" />
          Add Device
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Network Devices</CardTitle>
          <CardDescription>
            View and manage all registered network devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading devices...</span>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-8">
              <p className="text-red-500 mb-4">{error}</p>
              <Button onClick={fetchDevices} variant="outline">
                Retry
              </Button>
            </div>
          ) : devices.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8">
              <p className="text-muted-foreground mb-4">No devices found</p>
              <Button onClick={handleAddDevice} variant="outline">
                Add your first device
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Vendor</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Backup</TableHead>
                  <TableHead>Auto Backup</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {devices.map((device) => (
                  <TableRow key={device.id}>
                    <TableCell className="font-medium">{device.name}</TableCell>
                    <TableCell>{device.ip_address}</TableCell>
                    <TableCell className="capitalize">{device.device_type}</TableCell>
                    <TableCell>{device.vendor}</TableCell>
                    <TableCell>
                      <span className={`${getStatusColor(device.status)} capitalize`}>
                        {device.status}
                      </span>
                    </TableCell>
                    <TableCell>
                      {device.last_backup
                        ? new Date(device.last_backup).toLocaleString()
                        : "Never"}
                    </TableCell>
                    <TableCell>
                      {device.auto_backup_enabled ? (
                        <span className="text-green-500">Enabled</span>
                      ) : (
                        <span className="text-gray-500">Disabled</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleBackup(device.id)}
                          title="Trigger Backup"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditDevice(device)}
                          title="Edit Device"
                        >
                          <Settings className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteDevice(device.id)}
                          title="Delete Device"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <DeviceDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        device={selectedDevice}
        onSave={handleSaveDevice}
        mode={dialogMode}
      />
    </div>
  )
}
