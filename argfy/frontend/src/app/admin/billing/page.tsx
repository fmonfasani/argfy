"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { adminApi } from "@/lib/admin"

export default function AdminBillingPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) {
      router.push("/auth/login")
      return
    }
    if (user?.role === "admin") {
      adminApi.billing().then((r) => { setData(r.data); setLoading(false) }).catch(() => setLoading(false))
    }
  }, [user, authLoading, router])

  if (authLoading || loading) {
    return <div className="max-w-7xl mx-auto px-4 py-12 text-white">Cargando...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Facturación</h1>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="text-left px-4 py-3">Plan</th>
              <th className="text-left px-4 py-3">Estado</th>
              <th className="text-left px-4 py-3">Inicio</th>
              <th className="text-left px-4 py-3">Fin</th>
              <th className="text-left px-4 py-3">Cancelada</th>
            </tr>
          </thead>
          <tbody>
            {data.map((s: any) => (
              <tr key={s.id} className="border-b border-slate-700/50 text-white">
                <td className="px-4 py-3 capitalize font-semibold">{s.plan}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    s.status === "active" ? "bg-green-900/50 text-green-400" :
                    s.status === "cancelled" ? "bg-red-900/50 text-red-400" :
                    "bg-yellow-900/50 text-yellow-400"
                  }`}>{s.status}</span>
                </td>
                <td className="px-4 py-3 text-slate-400">{s.current_period_start ? new Date(s.current_period_start).toLocaleDateString() : "-"}</td>
                <td className="px-4 py-3 text-slate-400">{s.current_period_end ? new Date(s.current_period_end).toLocaleDateString() : "-"}</td>
                <td className="px-4 py-3 text-slate-400">{s.cancel_at_period_end ? "Sí" : "No"}</td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr><td colSpan={5} className="text-center text-slate-500 py-8">Sin historial de suscripciones</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
