// frontend/src/components/Footer.tsx
'use client'
import Link from 'next/link'

export default function Footer() {
  const contactInfo = [
    {
      label: "Ubicación",
      value: "Buenos Aires, AR",
      color: "text-white"
    },
    {
      label: "WhatsApp",
      value: "Disponible",
      color: "text-green-400"
    },
    {
      label: "Email",
      value: "contact@argfy.com",
      color: "text-blue-400"
    }
  ]

  const supportInfo = [
    {
      label: "API Documentation",
      value: "Coming Soon",
      color: "text-white"
    },
    {
      label: "Status",
      value: "Online",
      color: "text-emerald-400"
    },
    {
      label: "Uptime",
      value: "99.9%",
      color: "text-white"
    }
  ]

  const platformInfo = [
    {
      label: "Versión",
      value: "Demo v0.1",
      color: "text-white"
    },
    {
      label: "Indicadores",
      value: "25+",
      color: "text-amber-400"
    },
    {
      label: "Fuentes",
      value: "BCRA, INDEC",
      color: "text-white"
    }
  ]

  return (
    <footer className="py-16 bg-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">
            📞 Contact & Support
          </h2>
          <p className="text-lg text-slate-300">
            Conecta con nosotros para consultas, soporte técnico y colaboraciones
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* Contact Information */}
          <div className="bg-slate-700 rounded-lg p-6 border border-slate-600 hover:bg-slate-650 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Información de Contacto</h3>
            <div className="space-y-3">
              {contactInfo.map((item, index) => (
                <div key={index} className="flex justify-between">
                  <span className="text-slate-300">{item.label}</span>
                  <span className={`font-semibold ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Technical Support */}
          <div className="bg-slate-700 rounded-lg p-6 border border-slate-600 hover:bg-slate-650 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Soporte Técnico</h3>
            <div className="space-y-3">
              {supportInfo.map((item, index) => (
                <div key={index} className="flex justify-between">
                  <span className="text-slate-300">{item.label}</span>
                  <span className={`font-semibold ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Info */}
          <div className="bg-slate-700 rounded-lg p-6 border border-slate-600 hover:bg-slate-650 transition-colors">
            <h3 className="text-lg font-semibold text-white mb-4">Plataforma</h3>
            <div className="space-y-3">
              {platformInfo.map((item, index) => (
                <div key={index} className="flex justify-between">
                  <span className="text-slate-300">{item.label}</span>
                  <span className={`font-semibold ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="border-t border-slate-600 pt-8 mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h4 className="text-white font-semibold mb-4">Productos</h4>
              <ul className="space-y-2">
                <li><Link href="/dashboard" className="text-slate-300 hover:text-white transition-colors">Dashboard</Link></li>
                <li><Link href="/api" className="text-slate-300 hover:text-white transition-colors">API</Link></li>
                <li><Link href="/analytics" className="text-slate-300 hover:text-white transition-colors">Analytics</Link></li>
                <li><Link href="/alerts" className="text-slate-300 hover:text-white transition-colors">Alertas</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Mercados</h4>
              <ul className="space-y-2">
                <li><Link href="/forex" className="text-slate-300 hover:text-white transition-colors">Forex</Link></li>
                <li><Link href="/stocks" className="text-slate-300 hover:text-white transition-colors">Acciones</Link></li>
                <li><Link href="/bonds" className="text-slate-300 hover:text-white transition-colors">Bonos</Link></li>
                <li><Link href="/commodities" className="text-slate-300 hover:text-white transition-colors">Commodities</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Recursos</h4>
              <ul className="space-y-2">
                <li><Link href="/docs" className="text-slate-300 hover:text-white transition-colors">Documentación</Link></li>
                <li><Link href="/tutorials" className="text-slate-300 hover:text-white transition-colors">Tutoriales</Link></li>
                <li><Link href="/blog" className="text-slate-300 hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/help" className="text-slate-300 hover:text-white transition-colors">Ayuda</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Empresa</h4>
              <ul className="space-y-2">
                <li><Link href="/about" className="text-slate-300 hover:text-white transition-colors">Acerca de</Link></li>
                <li><Link href="/careers" className="text-slate-300 hover:text-white transition-colors">Carreras</Link></li>
                <li><Link href="/privacy" className="text-slate-300 hover:text-white transition-colors">Privacidad</Link></li>
                <li><Link href="/terms" className="text-slate-300 hover:text-white transition-colors">Términos</Link></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Social Media & Newsletter */}
        <div className="border-t border-slate-600 pt-8 mb-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <h4 className="text-white font-semibold mb-4">Síguenos</h4>
              <div className="flex space-x-4">
                <a href="#" className="text-slate-300 hover:text-white transition-colors">
                  <span className="sr-only">Twitter</span>
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a href="#" className="text-slate-300 hover:text-white transition-colors">
                  <span className="sr-only">LinkedIn</span>
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
                <a href="#" className="text-slate-300 hover:text-white transition-colors">
                  <span className="sr-only">GitHub</span>
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                </a>
              </div>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Newsletter</h4>
              <div className="flex max-w-md">
                <input
                  type="email"
                  placeholder="Tu email"
                  className="flex-1 px-4 py-2 bg-slate-700 text-white placeholder-slate-400 border border-slate-600 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <button className="px-6 py-2 bg-amber-600 text-slate-900 font-semibold rounded-r-lg hover:bg-amber-500 transition-colors">
                  Suscribirse
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Bottom */}
        <div className="border-t border-slate-600 pt-8 text-center">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-slate-700 border border-slate-600 rounded-lg flex items-center justify-center">
                <span className="text-amber-400 font-bold">A</span>
              </div>
              <h3 className="text-xl font-bold text-white">Argfy</h3>
              <span className="text-slate-400 text-sm">Demo v0.1</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-slate-400">
              <span>© 2024 Argfy. Financial Data Solutions</span>
              <div className="hidden md:flex items-center space-x-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span>Status: Operational</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}