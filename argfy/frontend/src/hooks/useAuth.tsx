"use client"
import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import type { AuthUser } from "@/lib/auth"
import { fetchMe, saveToken, getToken, clearToken } from "@/lib/auth"

interface AuthContextType {
  user: AuthUser | null
  loading: boolean
  setUser: (user: AuthUser | null, token?: string) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  setUser: () => {},
  logout: () => {},
  isAuthenticated: false,
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  const setUser = useCallback((user: AuthUser | null, token?: string) => {
    setUserState(user)
    if (token) saveToken(token)
    if (!user) clearToken()
  }, [])

  const logout = useCallback(() => {
    setUserState(null)
    clearToken()
  }, [])

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }
    fetchMe(token)
      .then((u) => setUserState(u))
      .catch(() => clearToken())
      .finally(() => setLoading(false))
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, setUser, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
