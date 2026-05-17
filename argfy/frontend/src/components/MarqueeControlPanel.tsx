// Componente opcional para controlar las marquesinas
'use client'
import { useState, useContext, createContext } from 'react'

// Context para configuraciones globales de marquesinas
export const MarqueeContext = createContext({
  theme: 'modern',
  speed: 'normal',
  effects: true,
  sounds: false,
  setTheme: (theme: string) => {},
  setSpeed: (speed: string) => {},
  setEffects: (effects: boolean) => {},
  setSounds: (sounds: boolean) => {},
})

export function MarqueeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState('modern')
  const [speed, setSpeed] = useState('normal')
  const [effects, setEffects] = useState(true)
  const [sounds, setSounds] = useState(false)

  return (
    <MarqueeContext.Provider value={{
      theme, speed, effects, sounds,
      setTheme, setSpeed, setEffects, setSounds
    }}>
      {children}
    </MarqueeContext.Provider>
  )
}

export default function MarqueeControlPanel() {
  const [isOpen, setIsOpen] = useState(false)
  const {
    theme, speed, effects, sounds,
    setTheme, setSpeed, setEffects, setSounds
  } = useContext(MarqueeContext)

  const themes = [
    { id: 'modern', name: 'Moderno', colors: 'bg-gradient-to-r from-blue-500 to-purple-500' },
    { id: 'professional', name: 'Profesional', colors: 'bg-gradient-to-r from-slate-600 to-slate-800' },
    { id: 'crypto', name: 'Crypto', colors: 'bg-gradient-to-r from-orange-500 to-yellow-500' },
    { id: 'fintech', name: 'Fintech', colors: 'bg-gradient-to-r from-indigo-500 to-purple-600' },
    { id: 'neon', name: 'Neon', colors: 'bg-gradient-to-r from-pink-500 to-cyan-500' }
  ]

  const speeds = [
    { id: 'slow', name: 'Lento', duration: '60s' },
    { id: 'normal', name: 'Normal', duration: '40s' },
    { id: 'fast', name: 'Rápido', duration: '20s' },
    { id: 'turbo', name: 'Turbo', duration: '10s' }
  ]

  return (
    <>
      {/* Botón flotante para abrir panel */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 flex items-center justify-center"
        title="Configurar Marquesinas"
      >
        <span className="text-xl">⚙️</span>
      </button>

      {/* Panel de control */}
      {isOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
          {/* Overlay */}
          <div 
            className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          ></div>

          {/* Panel */}
          <div className="relative bg-white rounded-2xl shadow-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-800">🎨 Control Marquesinas</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center hover:bg-slate-300 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Tema */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-700 mb-3">Tema Visual</h3>
              <div className="grid grid-cols-2 gap-2">
                {themes.map((themeOption) => (
                  <button
                    key={themeOption.id}
                    onClick={() => setTheme(themeOption.id)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      theme === themeOption.id 
                        ? 'border-blue-500 ring-2 ring-blue-200' 
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className={`w-full h-6 rounded mb-2 ${themeOption.colors}`}></div>
                    <div className="text-sm font-medium text-slate-700">{themeOption.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Velocidad */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-700 mb-3">Velocidad</h3>
              <div className="space-y-2">
                {speeds.map((speedOption) => (
                  <button
                    key={speedOption.id}
                    onClick={() => setSpeed(speedOption.id)}
                    className={`w-full p-3 rounded-lg border-2 text-left transition-all flex justify-between items-center ${
                      speed === speedOption.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <span className="font-medium">{speedOption.name}</span>
                    <span className="text-sm text-slate-500">{speedOption.duration}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Efectos */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-700 mb-3">Efectos</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between">
                  <span className="text-slate-600">Animaciones Visuales</span>
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={effects}
                      onChange={(e) => setEffects(e.target.checked)}
                      className="sr-only"
                    />
                    <div className={`w-12 h-6 rounded-full transition-colors ${
                      effects ? 'bg-blue-500' : 'bg-slate-300'
                    }`}>
                      <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                        effects ? 'translate-x-6' : 'translate-x-0.5'
                      } translate-y-0.5`}></div>
                    </div>
                  </div>
                </label>

                <label className="flex items-center justify-between">
                  <span className="text-slate-600">Sonidos</span>
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={sounds}
                      onChange={(e) => setSounds(e.target.checked)}
                      className="sr-only"
                    />
                    <div className={`w-12 h-6 rounded-full transition-colors ${
                      sounds ? 'bg-blue-500' : 'bg-slate-300'
                    }`}>
                      <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                        sounds ? 'translate-x-6' : 'translate-x-0.5'
                      } translate-y-0.5`}></div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* Preview */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-700 mb-3">Vista Previa</h3>
              <div className="border rounded-lg overflow-hidden">
                <div className={`py-2 px-4 ${
                  theme === 'modern' ? 'bg-gradient-to-r from-blue-500 to-purple-500' :
                  theme === 'professional' ? 'bg-gradient-to-r from-slate-600 to-slate-800' :
                  theme === 'crypto' ? 'bg-gradient-to-r from-orange-500 to-yellow-500' :
                  theme === 'fintech' ? 'bg-gradient-to-r from-indigo-500 to-purple-600' :
                  'bg-gradient-to-r from-pink-500 to-cyan-500'
                }`}>
                  <div className="text-white text-xs text-center">🎨 PREVIEW MARQUEE</div>
                </div>
                <div className="p-3 bg-slate-50 overflow-hidden">
                  <div className={`flex items-center space-x-4 ${
                    speed === 'slow' ? 'animate-pulse' :
                    speed === 'fast' ? 'animate-bounce' :
                    'animate-pulse'
                  }`}>
                    <div className="marquee-item positive flex items-center space-x-2">
                      <span>📊</span>
                      <span className="text-sm font-medium">EJEMPLO:</span>
                      <span className="text-sm font-bold">$1,234</span>
                      <span className="text-xs text-green-600">+2.1%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Acciones */}
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setTheme('modern')
                  setSpeed('normal')
                  setEffects(true)
                  setSounds(false)
                }}
                className="flex-1 py-2 px-4 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
              >
                Reset
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="flex-1 py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
              >
                Aplicar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CSS dinámico */}
      <style jsx global>{`
        .marquee-track {
          animation-duration: ${
            speed === 'slow' ? '60s' :
            speed === 'fast' ? '20s' :
            speed === 'turbo' ? '10s' :
            '40s'
          } !important;
        }
        
        .marquee-item {
          ${effects ? `
            transition: all 0.3s ease !important;
            backdrop-filter: blur(4px) !important;
          ` : `
            transition: none !important;
            backdrop-filter: none !important;
          `}
        }
        
        ${theme === 'neon' ? `
          .marquee-container {
            filter: drop-shadow(0 0 10px rgba(236, 72, 153, 0.5)) !important;
          }
          .marquee-item {
            border: 1px solid rgba(236, 72, 153, 0.3) !important;
            box-shadow: 0 0 20px rgba(236, 72, 153, 0.2) !important;
          }
        ` : ''}
      `}</style>
    </>
  )
}