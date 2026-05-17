"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import Link from "next/link"

export default function AccountTeamPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
    }
  }, [user, authLoading, router])

  if (authLoading) {
    return <div className="max-w-4xl mx-auto px-4 py-12 text-white">Cargando...</div>
  }

  if (!user) return null

  const isEnterprise = user.subscription?.plan === "enterprise"

  if (!isEnterprise) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h1 className="text-3xl font-bold text-white mb-8">Equipo</h1>
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-12">
          <div className="text-6xl mb-4">🔒</div>
          <h2 className="text-2xl font-bold text-white mb-2">Funcionalidad exclusiva Enterprise</h2>
          <p className="text-slate-400 mb-8 max-w-md mx-auto">
            La gestión de equipo e invitaciones está disponible solo para planes Enterprise.
            Actualizá tu plan para invitar colaboradores.
          </p>
          <Link
            href="/pricing"
            className="inline-block px-8 py-3 bg-amber-600 text-slate-900 font-semibold rounded-lg hover:bg-amber-500 transition-colors"
          >
            Ver planes
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Equipo</h1>
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 text-center">
        <p className="text-slate-400">La gestión de miembros del equipo estará disponible próximamente.</p>
      </div>
    </div>
  )
}
