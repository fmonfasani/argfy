"use client"
import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { googleAuth } from "@/lib/auth"
import { useAuth } from "@/hooks/useAuth"

export default function GoogleCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { setUser } = useAuth()
  const [error, setError] = useState("")

  useEffect(() => {
    const code = searchParams.get("code")
    if (!code) {
      setError("No authorization code received")
      return
    }

    googleAuth(code)
      .then((res) => {
        setUser(res.user, res.access_token)
        router.push("/account")
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Google authentication failed")
      })
  }, [searchParams, router, setUser])

  if (error) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="bg-red-900/30 border border-red-800 text-red-400 rounded-lg px-6 py-4">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="text-white text-lg">Autenticando con Google...</div>
    </div>
  )
}
