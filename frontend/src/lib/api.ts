// frontend/src/lib/api.ts
type Method = 'GET' | 'POST' | 'PUT' | 'DELETE'

export interface RequestConfig extends RequestInit {
  params?: Record<string, any>          // ?q=foo&limit=10
  timeout?: number                      // ms
}

// ---- Interceptor types ---------------------------------------------------
type RequestInterceptor = (config: RequestConfig & { url: string }) => Promise<RequestConfig> | RequestConfig
type ResponseInterceptor = (resp: Response) => Promise<Response> | Response
type ErrorInterceptor = (err: any) => any
// --------------------------------------------------------------------------

const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

class FetchClient {
  private requestInterceptors: RequestInterceptor[] = []
  private responseInterceptors: ResponseInterceptor[] = []
  private errorInterceptors: ErrorInterceptor[] = []

  private async request<T>(
    method: Method,
    url: string,
    cfg: RequestConfig = {}
  ): Promise<T> {
    // assemble full URL + query string
    const fullURL = new URL(`${API_BASE_URL}/api/v1${url}`)
    if (cfg.params) Object.entries(cfg.params).forEach(([k, v]) => fullURL.searchParams.append(k, String(v)))

    // default headers
    const init: RequestConfig = {
      method,
      headers: { 'Content-Type': 'application/json', ...cfg.headers },
      ...cfg,
    }

    // run request interceptors
    for (const fn of this.requestInterceptors) {
      Object.assign(init, await fn({ url: fullURL.toString(), ...init }))
    }

    // timeout helper
    const ctrl = new AbortController()
    const timeout = init.timeout ?? 10000
    const id = setTimeout(() => ctrl.abort(), timeout)
    init.signal = ctrl.signal

    try {
      const response = await fetch(fullURL, init)
      clearTimeout(id)

      // run response interceptors
      for (const fn of this.responseInterceptors) await fn(response)

      if (!response.ok) {
        const err: any = new Error(`HTTP ${response.status}`)
        err.response = response
        throw err
      }
      return (await response.json()) as T
    } catch (err) {
      // run error interceptors
      for (const fn of this.errorInterceptors) err = await fn(err)
      throw err
    }
  }

  // public helpers (mimic axios)
  get  = <T>(url: string, cfg?: RequestConfig) => this.request<T>('GET', url, cfg)
  post = <T>(url: string, data?: any, cfg: RequestConfig = {}) =>
    this.request<T>('POST', url, { ...cfg, body: JSON.stringify(data) })
  put  = <T>(url: string, data?: any, cfg: RequestConfig = {}) =>
    this.request<T>('PUT', url, { ...cfg, body: JSON.stringify(data) })
  delete = <T>(url: string, cfg?: RequestConfig) => this.request<T>('DELETE', url, cfg)

  // interceptors API
  interceptors = {
    request: {
      use: (fn: RequestInterceptor) => this.requestInterceptors.push(fn),
    },
    response: {
      use: (onOk: ResponseInterceptor, onErr?: ErrorInterceptor) => {
        this.responseInterceptors.push(onOk)
        if (onErr) this.errorInterceptors.push(onErr)
      },
    },
  }
}

export const apiClient = new FetchClient()
