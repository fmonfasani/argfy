"use client"

import { useEffect, useState } from "react"
import { SunIcon, MoonIcon } from "@heroicons/react/24/outline"

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const [dark, setDark] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem("theme")
    const prefersDark = stored ? stored === "dark" : true
    setDark(prefersDark)
    document.documentElement.classList.toggle("dark", prefersDark)
    setMounted(true)
  }, [])

  function toggle() {
    const next = !dark
    setDark(next)
    document.documentElement.classList.toggle("dark", next)
    localStorage.setItem("theme", next ? "dark" : "light")
  }

  if (!mounted) return <div className="w-9 h-9" />

  return (
    <button
      onClick={toggle}
      className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
      title={dark ? "Modo claro" : "Modo oscuro"}
    >
      {dark ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
    </button>
  )
}
