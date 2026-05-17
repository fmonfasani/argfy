"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { adminApi, type AdminUser } from "@/lib/admin"

export default function AdminTeamPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [users, setUsers] = useState<AdminUser[]>([])
  const [inviteEmail, setInviteEmail] = useState("")
  const [msg, setMsg] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) {
      router.push("/auth/login")
      return
    }
    if (user?.role === "admin") {
      adminApi.users().then((r) => { setUsers(r.data); setLoading(false) }).catch(() => setLoading(false))
    }
  }, [user, authLoading, router])

  const invite = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg("")
    try {
      const res = await adminApi.createInvitation(inviteEmail)
      setMsg(`Invitación enviada a ${res.email} (token: ${res.token.slice(0, 12)}...)`)
      setInviteEmail("")
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed to invite")
    }
  }

  if (authLoading || loading) {
    return <div className="max-w-7xl mx-auto px-4 py-12 text-white">Cargando...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Equipo</h1>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Invitar miembro</h2>
        <form onSubmit={invite} className="flex gap-3">
          <input
            type="email"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            placeholder="email@ejemplo.com"
            required
            className="flex-1 px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
          <button type="submit" className="px-6 py-2 bg-amber-600 text-slate-900 font-semibold rounded-lg hover:bg-amber-500 transition-colors">
            Invitar
          </button>
        </form>
        {msg && <div className="mt-3 text-sm text-amber-400">{msg}</div>}
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="text-left px-4 py-3">Email</th>
              <th className="text-left px-4 py-3">Nombre</th>
              <th className="text-left px-4 py-3">Rol</th>
              <th className="text-left px-4 py-3">Estado</th>
              <th className="text-left px-4 py-3">Creado</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-slate-700/50 text-white">
                <td className="px-4 py-3">{u.email}</td>
                <td className="px-4 py-3 text-slate-400">{u.nombre || "-"}</td>
                <td className="px-4 py-3 capitalize">{u.role}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs ${u.is_active ? "bg-green-900/50 text-green-400" : "bg-red-900/50 text-red-400"}`}>
                    {u.is_active ? "active" : "inactive"}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-400">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
