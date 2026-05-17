"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { adminApi, type ApiKeyInfo } from "@/lib/admin"

export default function AdminApiKeysPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [keys, setKeys] = useState<ApiKeyInfo[]>([])
  const [newKeyName, setNewKeyName] = useState("")
  const [newKeyRaw, setNewKeyRaw] = useState("")
  const [msg, setMsg] = useState("")
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const r = await adminApi.apiKeys()
      setKeys(r.data)
    } catch { /* ignore */ }
    setLoading(false)
  }

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) {
      router.push("/auth/login")
      return
    }
    if (user?.role === "admin") load()
  }, [user, authLoading, router])

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg("")
    setNewKeyRaw("")
    try {
      const res = await adminApi.createApiKey(newKeyName)
      setNewKeyRaw(res.raw_key)
      setNewKeyName("")
      setMsg("Key created — copy it now, it won't be shown again!")
      load()
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed to create key")
    }
  }

  const revoke = async (id: string) => {
    if (!confirm("Revoke this API key?")) return
    try {
      await adminApi.revokeApiKey(id)
      load()
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed to revoke")
    }
  }

  if (authLoading || loading) {
    return <div className="max-w-7xl mx-auto px-4 py-12 text-white">Cargando...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">API Keys</h1>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Crear API Key</h2>
        <form onSubmit={create} className="flex gap-3">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="Nombre para identificar la key"
            required
            className="flex-1 px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
          <button type="submit" className="px-6 py-2 bg-amber-600 text-slate-900 font-semibold rounded-lg hover:bg-amber-500 transition-colors">
            Crear
          </button>
        </form>
        {newKeyRaw && (
          <div className="mt-4 bg-amber-900/30 border border-amber-700 rounded-lg p-4">
            <div className="text-amber-400 text-sm font-semibold mb-1">⚠️ Copiala ahora — no se mostrará de nuevo</div>
            <code className="text-white text-sm break-all">{newKeyRaw}</code>
          </div>
        )}
      </div>

      {msg && !newKeyRaw && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm text-amber-400 mb-6">{msg}</div>
      )}

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="text-left px-4 py-3">Nombre</th>
              <th className="text-left px-4 py-3">Prefijo</th>
              <th className="text-left px-4 py-3">Último uso</th>
              <th className="text-left px-4 py-3">Creado</th>
              <th className="text-left px-4 py-3">Acción</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((k) => (
              <tr key={k.id} className="border-b border-slate-700/50 text-white">
                <td className="px-4 py-3">{k.name}</td>
                <td className="px-4 py-3 font-mono text-slate-400">{k.key_prefix}...</td>
                <td className="px-4 py-3 text-slate-400">{k.last_used ? new Date(k.last_used).toLocaleString() : "never"}</td>
                <td className="px-4 py-3 text-slate-400">{k.created_at ? new Date(k.created_at).toLocaleDateString() : "-"}</td>
                <td className="px-4 py-3">
                  <button onClick={() => revoke(k.id)} className="text-red-400 hover:text-red-300 text-xs">
                    Revocar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {keys.length === 0 && (
          <div className="text-center text-slate-500 py-8">No hay API keys creadas</div>
        )}
      </div>
    </div>
  )
}
