const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

interface Device {
  id: number
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
  status: string
  last_backup: string | null
  auto_backup_enabled: boolean
  backup_interval: number
  description?: string
  location?: string
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    // Load token from localStorage on init
    this.token = localStorage.getItem("access_token")
  }

  setToken(token: string | null) {
    this.token = token
    if (token) {
      localStorage.setItem("access_token", token)
    } else {
      localStorage.removeItem("access_token")
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      headers,
      ...options,
    })

    if (!response.ok) {
      if (response.status === 401) {
        // Unauthorized - clear token and redirect to login
        this.setToken(null)
        window.location.href = "/login"
      }
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Device endpoints
  async getDevices(skip: number = 0, limit: number = 100): Promise<Device[]> {
    return this.request<Device[]>(`/devices/?skip=${skip}&limit=${limit}`)
  }

  async getDevice(id: number): Promise<Device> {
    return this.request<Device>(`/devices/${id}`)
  }

  async createDevice(device: Partial<Device>): Promise<Device> {
    return this.request<Device>("/devices/", {
      method: "POST",
      body: JSON.stringify(device),
    })
  }

  async updateDevice(id: number, device: Partial<Device>): Promise<Device> {
    return this.request<Device>(`/devices/${id}`, {
      method: "PUT",
      body: JSON.stringify(device),
    })
  }

  async deleteDevice(id: number): Promise<void> {
    return this.request<void>(`/devices/${id}`, {
      method: "DELETE",
    })
  }

  async testConnection(id: number): Promise<any> {
    return this.request<any>(`/devices/${id}/test-connection`, {
      method: "POST",
    })
  }

  async triggerBackup(id: number): Promise<any> {
    return this.request<any>(`/devices/${id}/backup`, {
      method: "POST",
    })
  }

  // Configuration endpoints
  async getDeviceConfigurations(deviceId: number, skip: number = 0, limit: number = 50): Promise<any[]> {
    return this.request<any[]>(`/configurations/device/${deviceId}?skip=${skip}&limit=${limit}`)
  }

  async getLatestConfiguration(deviceId: number): Promise<any> {
    return this.request<any>(`/configurations/device/${deviceId}/latest`)
  }

  async getConfigurationDiff(deviceId: number, versionA: number, versionB: number): Promise<any> {
    return this.request<any>(`/configurations/device/${deviceId}/diff?version_a=${versionA}&version_b=${versionB}`)
  }

  // Backup job endpoints
  async getBackupJobs(skip: number = 0, limit: number = 100, deviceId?: number): Promise<any[]> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (deviceId) params.append("device_id", deviceId.toString())
    return this.request<any[]>(`/backup-jobs/?${params}`)
  }

  async getBackupJob(jobId: number): Promise<any> {
    return this.request<any>(`/backup-jobs/${jobId}`)
  }

  async getBackupSummary(): Promise<any> {
    return this.request<any>("/backup-jobs/summary/overview")
  }

  async triggerDeviceBackup(deviceId: number): Promise<any> {
    return this.request<any>(`/backup-jobs/device/${deviceId}/trigger`, {
      method: "POST",
    })
  }

  async triggerAllBackups(): Promise<any> {
    return this.request<any>("/backup-jobs/trigger-all", {
      method: "POST",
    })
  }

  // Authentication endpoints
  async register(username: string, email: string, password: string): Promise<any> {
    return this.request<any>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password, is_active: true, is_admin: false }),
    })
  }

  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData()
    formData.append("username", username)
    formData.append("password", password)

    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Login failed: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    this.setToken(data.access_token)
    return data
  }

  async logout(): Promise<any> {
    this.setToken(null)
    return Promise.resolve({ message: "Logged out" })
  }

  async getCurrentUser(): Promise<any> {
    return this.request<any>("/auth/me")
  }
}

export const api = new ApiClient()
export type { Device }
