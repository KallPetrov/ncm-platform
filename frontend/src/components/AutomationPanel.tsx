import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { api, type Device } from "@/lib/api"
import { Play, RefreshCw, ShieldCheck } from "lucide-react"

interface AutomationTemplate {
  name: string
  content: string
}

export function AutomationPanel() {
  const [templates, setTemplates] = React.useState<AutomationTemplate[]>([])
  const [devices, setDevices] = React.useState<Device[]>([])
  const [selectedTemplateName, setSelectedTemplateName] = React.useState("")
  const [templateContent, setTemplateContent] = React.useState("")
  const [variablesText, setVariablesText] = React.useState('{"device_name":"automation-router"}')
  const [selectedDeviceIds, setSelectedDeviceIds] = React.useState<number[]>([])
  const [loading, setLoading] = React.useState(false)
  const [message, setMessage] = React.useState<string | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    void loadData()
  }, [])

  const loadData = async () => {
    try {
      const [templatesData, devicesData] = await Promise.all([
        api.getAutomationTemplates(),
        api.getDevices(0, 100),
      ])
      setTemplates(templatesData)
      setDevices(devicesData)
      if (templatesData.length > 0) {
        const firstTemplate = templatesData[0]
        setSelectedTemplateName(firstTemplate.name)
        setTemplateContent(firstTemplate.content)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load automation data")
    }
  }

  const handleTemplateChange = (templateName: string) => {
    const template = templates.find((item) => item.name === templateName)
    setSelectedTemplateName(templateName)
    setTemplateContent(template?.content || "")
  }

  const handleValidate = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.validateAutomationTemplate(templateContent)
      setMessage(result.valid ? "Template is valid" : `Template validation failed: ${result.error}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Validation failed")
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async () => {
    try {
      setLoading(true)
      setError(null)
      const variables = JSON.parse(variablesText || "{}")
      const result = await api.applyAutomationTemplate(selectedDeviceIds, templateContent, variables)
      setMessage(`Applied to ${result.total_devices} device(s)`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to apply automation template")
    } finally {
      setLoading(false)
    }
  }

  const handleDeviceSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const values = Array.from(event.target.selectedOptions, (option) => Number(option.value))
    setSelectedDeviceIds(values)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="h-5 w-5" />
            Automation Templates
          </CardTitle>
          <CardDescription>
            Validate and apply real configuration templates to selected devices.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Template</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={selectedTemplateName}
              onChange={(event) => handleTemplateChange(event.target.value)}
            >
              {templates.map((template) => (
                <option key={template.name} value={template.name}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Template content</label>
            <textarea
              className="min-h-[220px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
              value={templateContent}
              onChange={(event) => setTemplateContent(event.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Variables (JSON)</label>
            <textarea
              className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
              value={variablesText}
              onChange={(event) => setVariablesText(event.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Target devices</label>
            <select
              className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              multiple
              value={selectedDeviceIds.map((id) => id.toString())}
              onChange={handleDeviceSelection}
            >
              {devices.map((device) => (
                <option key={device.id} value={device.id}>
                  {device.name} ({device.ip_address})
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button onClick={handleValidate} disabled={loading} variant="outline">
              {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <ShieldCheck className="mr-2 h-4 w-4" />}
              Validate
            </Button>
            <Button onClick={handleApply} disabled={loading || selectedDeviceIds.length === 0}>
              {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Apply to selected devices
            </Button>
          </div>

          {message && (
            <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700">
              {message}
            </div>
          )}
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Available templates</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {templates.map((template) => (
            <div key={template.name} className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <div className="font-medium">{template.name}</div>
                <div className="text-sm text-muted-foreground">Jinja2 ready template</div>
              </div>
              <Badge variant="secondary">Ready</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
