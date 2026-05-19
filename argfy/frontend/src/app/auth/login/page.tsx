'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { login } from '@/lib/auth'
import { useAuth } from '@/hooks/useAuth'
import { Input, Button, Alert } from '@/components/ui'

export default function LoginPage() {
  const router = useRouter()
  const { setUser } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await login(email, password)
      setUser(res.user, res.access_token)
      router.push('/')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
          <h1 className="text-2xl font-bold text-white mb-2">Iniciar sesión</h1>
          <p className="text-slate-400 mb-6">Accedé a tu cuenta de Argfy</p>

          {error && (
            <Alert variant="error" onClose={() => setError('')} className="mb-6">
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              placeholder="tu@email.com"
            />
            <Input
              label="Contraseña"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
            <Button variant="primary" type="submit" className="w-full" loading={loading}>
              Ingresar
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-400">
            ¿No tenés cuenta?{' '}
            <Link href="/auth/register" className="text-amber-400 hover:underline">
              Registrate
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
