"use client"
import { useAuth } from "@/hooks/useAuth"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function AccountPage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login")
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="text-white text-lg">Cargando...</div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Mi cuenta</h1>
        <button
          onClick={() => { logout(); router.push("/") }}
          className="px-4 py-2 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
        >
          Cerrar sesión
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-amber-400 text-sm font-semibold mb-1">Plan actual</h3>
          <p className="text-2xl font-bold text-white capitalize">{user.subscription?.plan || "free"}</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-amber-400 text-sm font-semibold mb-1">Rol</h3>
          <p className="text-2xl font-bold text-white capitalize">{user.role}</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-amber-400 text-sm font-semibold mb-1">Email</h3>
          <p className="text-lg font-bold text-white truncate">{user.email}</p>
        </div>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-4">Perfil</h2>
        <dl className="space-y-3">
          <div className="flex justify-between">
            <dt className="text-slate-400">Nombre</dt>
            <dd className="text-white">{user.nombre}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-400">Email</dt>
            <dd className="text-white">{user.email}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-400">Rol</dt>
            <dd className="text-white capitalize">{user.role}</dd>
          </div>
        </dl>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href="/pricing" className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-amber-500/50 transition-all text-center">
          <h3 className="text-white font-semibold mb-2">Actualizar plan</h3>
          <p className="text-slate-400 text-sm">Explorá los planes Pro y Enterprise</p>
        </Link>
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center opacity-50 cursor-not-allowed">
          <h3 className="text-white font-semibold mb-2">API Keys</h3>
          <p className="text-slate-400 text-sm">Próximamente</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center opacity-50 cursor-not-allowed">
          <h3 className="text-white font-semibold mb-2">Equipo</h3>
          <p className="text-slate-400 text-sm">Próximamente</p>
        </div>
      </div>
    </div>
  )
}
