"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { adminApi, type AdminOverview } from "@/lib/admin"
import Link from "next/link"

export default function AdminDashboardPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [data, setData] = useState<AdminOverview | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      router.push("/auth/login")
      return
    }
    if (user?.role === "admin") {
      adminApi.overview()
        .then(setData)
        .catch((e) => setError(e.message))
    }
  }, [user, loading, router])

  if (loading || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-48" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-slate-700 rounded-xl" />)}
          </div>
        </div>
      </div>
    )
  }

  if (error) return <div className="max-w-7xl mx-auto px-4 py-12 text-red-400">{error}</div>

  const cards = [
    { label: "Plan actual", value: data.plan.toUpperCase(), color: "text-amber-400" },
    { label: "API calls hoy", value: data.api_calls_today.toLocaleString(), color: "text-blue-400" },
    { label: "Usuarios activos", value: data.active_users.toString(), color: "text-green-400" },
    { label: "ETL runs hoy", value: data.etl_runs_today.toString(), color: "text-purple-400" },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Admin Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <div className="text-sm text-slate-400 mb-1">{c.label}</div>
            <div className={`text-2xl font-bold ${c.color}`}>{c.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/admin/etl" className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-amber-500/50 transition-all">
          <h3 className="text-white font-semibold mb-1">ETL Jobs</h3>
          <p className="text-slate-400 text-sm">Historial y disparo manual</p>
        </Link>
        <Link href="/admin/team" className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-amber-500/50 transition-all">
          <h3 className="text-white font-semibold mb-1">Equipo</h3>
          <p className="text-slate-400 text-sm">Miembros e invitaciones</p>
        </Link>
        <Link href="/admin/api-keys" className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-amber-500/50 transition-all">
          <h3 className="text-white font-semibold mb-1">API Keys</h3>
          <p className="text-slate-400 text-sm">Administrar accesos</p>
        </Link>
        <Link href="/admin/billing" className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-amber-500/50 transition-all">
          <h3 className="text-white font-semibold mb-1">Facturación</h3>
          <p className="text-slate-400 text-sm">Historial de suscripciones</p>
        </Link>
      </div>
    </div>
  )
}
