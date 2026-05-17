"use client"
import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { adminApi, type ETLRunInfo, type ETLStatus } from "@/lib/admin"

export default function AdminETLPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [runs, setRuns] = useState<ETLRunInfo[]>([])
  const [status, setStatus] = useState<ETLStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [triggerMsg, setTriggerMsg] = useState("")

  const load = useCallback(async () => {
    try {
      const [r, s] = await Promise.all([adminApi.etlLastRuns(), adminApi.etlStatus()])
      setRuns(r.data)
      setStatus(s)
    } catch { /* ignore */ }
    setLoading(false)
  }, [])

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) {
      router.push("/auth/login")
      return
    }
    if (user?.role === "admin") load()
  }, [user, authLoading, router, load])

  const trigger = async (job: string) => {
    setTriggerMsg(`Triggering ${job}...`)
    try {
      const res = await adminApi.etlTrigger(job)
      setTriggerMsg(res.message)
      load()
    } catch (e: unknown) {
      setTriggerMsg(e instanceof Error ? e.message : "Trigger failed")
    }
  }

  if (authLoading || loading) {
    return <div className="max-w-7xl mx-auto px-4 py-12 text-white">Cargando...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-2">ETL Jobs</h1>
      <p className="text-slate-400 mb-6">
        Scheduler: {status?.scheduler_running ? "🟢 Running" : "🔴 Stopped"}
      </p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-8">
        {status?.registered_jobs.map((job) => {
          const last = status.last_runs[job]
          return (
            <div key={job} className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
              <div className="text-white font-semibold text-sm mb-1">{job}</div>
              <div className={`text-xs ${last?.status === "success" ? "text-green-400" : last?.status === "running" ? "text-yellow-400" : "text-slate-500"}`}>
                {last?.status || "never run"}
              </div>
              {last?.duration_ms != null && (
                <div className="text-xs text-slate-500">{last.duration_ms}ms</div>
              )}
              <button
                onClick={() => trigger(job)}
                className="mt-2 text-xs bg-amber-600 text-slate-900 px-3 py-1 rounded hover:bg-amber-500 transition-colors"
              >
                Trigger
              </button>
            </div>
          )
        })}
      </div>

      {triggerMsg && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm text-amber-400 mb-6">
          {triggerMsg}
        </div>
      )}

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="text-left px-4 py-3">Job</th>
              <th className="text-left px-4 py-3">Trigger</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="text-left px-4 py-3">Duration</th>
              <th className="text-left px-4 py-3">Started</th>
              <th className="text-left px-4 py-3">Rows</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id} className="border-b border-slate-700/50 text-white">
                <td className="px-4 py-3">{r.job_name}</td>
                <td className="px-4 py-3 text-slate-400">{r.trigger}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    r.status === "success" ? "bg-green-900/50 text-green-400" :
                    r.status === "running" ? "bg-yellow-900/50 text-yellow-400" :
                    "bg-red-900/50 text-red-400"
                  }`}>{r.status}</span>
                </td>
                <td className="px-4 py-3 text-slate-400">{r.duration_ms != null ? `${r.duration_ms}ms` : "-"}</td>
                <td className="px-4 py-3 text-slate-400">{r.started_at ? new Date(r.started_at).toLocaleString() : "-"}</td>
                <td className="px-4 py-3 text-slate-400">{r.rows_inserted}↑ {r.rows_updated}↻</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
