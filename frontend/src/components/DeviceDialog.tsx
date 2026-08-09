import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface DeviceDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  device?: {
    id?: number
    name: string
    ip_address: string
    device_type: string
    vendor: string
    model: string
    protocol: string
    port: number
    username: string
    password: string
    enable_password?: string
    backup_interval: number
    auto_backup_enabled: boolean
    description?: string
    location?: string
  }
  onSave: (device: any) => void
  mode: "create" | "edit"
}

export function DeviceDialog({
  open,
  onOpenChange,
  device,
  onSave,
  mode,
}: DeviceDialogProps) {
  const [formData, setFormData] = React.useState(
    device || {
      name: "",
      ip_address: "",
      device_type: "other",
      vendor: "",
      model: "",
      protocol: "ssh",
      port: 22,
      username: "",
      password: "",
      enable_password: "",
      backup_interval: 3600,
      auto_backup_enabled: true,
      description: "",
      location: "",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === "create" ? "Add New Device" : "Edit Device"}
          </DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "Add a new network device to the platform."
              : "Edit the device configuration."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Device Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ip_address">IP Address *</Label>
                <Input
                  id="ip_address"
                  value={formData.ip_address}
                  onChange={(e) =>
                    setFormData({ ...formData, ip_address: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="device_type">Device Type</Label>
                <select
                  id="device_type"
                  value={formData.device_type}
                  onChange={(e) =>
                    setFormData({ ...formData, device_type: e.target.value })
                  }
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="router">Router</option>
                  <option value="switch">Switch</option>
                  <option value="firewall">Firewall</option>
                  <option value="wireless">Wireless</option>
                  <option value="load_balancer">Load Balancer</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vendor">Vendor</Label>
                <Input
                  id="vendor"
                  value={formData.vendor}
                  onChange={(e) =>
                    setFormData({ ...formData, vendor: e.target.value })
                  }
                  placeholder="e.g., Cisco, MikroTik, Juniper"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="model">Model</Label>
                <Input
                  id="model"
                  value={formData.model}
                  onChange={(e) =>
                    setFormData({ ...formData, model: e.target.value })
                  }
                  placeholder="e.g., ISR 4431, CCR1036"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="protocol">Protocol</Label>
                <select
                  id="protocol"
                  value={formData.protocol}
                  onChange={(e) =>
                    setFormData({ ...formData, protocol: e.target.value })
                  }
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="ssh">SSH</option>
                  <option value="telnet">Telnet</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="port">Port</Label>
                <Input
                  id="port"
                  type="number"
                  value={formData.port}
                  onChange={(e) =>
                    setFormData({ ...formData, port: parseInt(e.target.value) })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="username">Username *</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) =>
                    setFormData({ ...formData, username: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="password">Password *</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="enable_password">Enable Password</Label>
                <Input
                  id="enable_password"
                  type="password"
                  value={formData.enable_password}
                  onChange={(e) =>
                    setFormData({ ...formData, enable_password: e.target.value })
                  }
                  placeholder="For Cisco devices"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="backup_interval">Backup Interval (seconds)</Label>
                <Input
                  id="backup_interval"
                  type="number"
                  value={formData.backup_interval}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      backup_interval: parseInt(e.target.value),
                    })
                  }
                />
              </div>
              <div className="space-y-2 flex items-center pt-6">
                <input
                  id="auto_backup_enabled"
                  type="checkbox"
                  checked={formData.auto_backup_enabled}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      auto_backup_enabled: e.target.checked,
                    })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="auto_backup_enabled" className="ml-2">
                  Auto Backup Enabled
                </Label>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={formData.location}
                  onChange={(e) =>
                    setFormData({ ...formData, location: e.target.value })
                  }
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">
              {mode === "create" ? "Add Device" : "Save Changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
