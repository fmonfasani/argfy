"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { userApi, type BillingInfo } from "@/lib/user"

export default function AccountBillingPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [billing, setBilling] = useState<BillingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [msg, setMsg] = useState("")

  const load = async () => {
    try {
      const data = await userApi.billing()
      setBilling(data)
    } catch { /* ignore */ }
    setLoading(false)
  }

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
      return
    }
    if (user) load()
  }, [user, authLoading, router])

  const handleCancel = async () => {
    if (!confirm("¿Cancelar la suscripción al final del período?")) return
    try {
      const res = await userApi.cancelSubscription()
      setMsg(res.message)
      load()
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Error al cancelar")
    }
  }

  if (authLoading || loading) {
    return <div className="max-w-4xl mx-auto px-4 py-12 text-white">Cargando...</div>
  }

  const isFree = billing?.plan === "free"
  const isCancelled = billing?.cancel_at_period_end

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Facturación</h1>

      {msg && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm text-amber-400 mb-6">{msg}</div>
      )}

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-amber-400 text-sm font-semibold mb-1">Plan actual</h3>
            <p className="text-2xl font-bold text-white capitalize">{billing?.plan || "free"}</p>
          </div>
          <div>
            <h3 className="text-amber-400 text-sm font-semibold mb-1">Estado</h3>
            <span className={`inline-block px-3 py-1 rounded text-sm font-semibold ${
              billing?.status === "active" && !isCancelled ? "bg-green-900/50 text-green-400" :
              isCancelled ? "bg-yellow-900/50 text-yellow-400" :
              "bg-slate-700 text-slate-300"
            }`}>
              {isCancelled ? "Cancelada (fin de período)" : billing?.status || "active"}
            </span>
          </div>
          {billing?.current_period_end && (
            <div>
              <h3 className="text-amber-400 text-sm font-semibold mb-1">Próximo vencimiento</h3>
              <p className="text-white">{new Date(billing.current_period_end).toLocaleDateString()}</p>
            </div>
          )}
          {billing?.current_period_start && (
            <div>
              <h3 className="text-amber-400 text-sm font-semibold mb-1">Inicio del período</h3>
              <p className="text-white">{new Date(billing.current_period_start).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      </div>

      {isFree ? (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center">
          <h2 className="text-xl font-bold text-white mb-2">Plan gratuito</h2>
          <p className="text-slate-400 mb-6">Actualizá a Pro o Enterprise para acceder a más funcionalidades.</p>
          <a
            href="/pricing"
            className="inline-block px-8 py-3 bg-amber-600 text-slate-900 font-semibold rounded-lg hover:bg-amber-500 transition-colors"
          >
            Ver planes
          </a>
        </div>
      ) : (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">Administrar suscripción</h2>
          <p className="text-slate-400 mb-6">
            {isCancelled
              ? "Tu suscripción se canceló y seguirá activa hasta el fin del período actual."
              : "Podés cancelar tu suscripción al final del período actual."}
          </p>
          {!isCancelled && (
            <button
              onClick={handleCancel}
              className="px-6 py-2 border border-red-600 text-red-400 rounded-lg hover:bg-red-900/30 transition-colors"
            >
              Cancelar suscripción
            </button>
          )}
        </div>
      )}
    </div>
  )
}
