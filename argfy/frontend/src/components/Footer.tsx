'use client'
import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="py-12 bg-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-slate-700 border border-slate-600 rounded-lg flex items-center justify-center">
                <span className="text-amber-400 font-bold">A</span>
              </div>
              <h3 className="text-xl font-bold text-white">Argfy</h3>
            </div>
            <p className="text-slate-400 text-sm">
              Screener profesional de CEDEARs y acciones BYMA con datos fundamentalistas de SEC.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Plataforma</h4>
            <ul className="space-y-2">
              <li><Link href="/cedears" className="text-slate-300 hover:text-white transition-colors text-sm">CEDEARs</Link></li>
              <li><Link href="/pricing" className="text-slate-300 hover:text-white transition-colors text-sm">Planes</Link></li>
              <li><Link href="/account" className="text-slate-300 hover:text-white transition-colors text-sm">Mi cuenta</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4">Contacto</h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>Buenos Aires, AR</li>
              <li>contact@argfy.com</li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                Status: Operational
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="border-t border-slate-700 pt-6">
          <p className="text-xs text-slate-500 text-center max-w-4xl mx-auto leading-relaxed">
            La información provista no constituye asesoramiento financiero ni recomendación de inversión.
            Los datos son provistos &quot;as-is&quot; con fines informativos. Consulte a un agente registrado ante la
            Comisión Nacional de Valores (CNV) antes de tomar decisiones de inversión. Las inversiones en
            CEDEARs y acciones conllevan riesgo de pérdida de capital.
          </p>
        </div>

        <div className="border-t border-slate-700 pt-6 mt-6 text-center text-sm text-slate-400">
          © 2024 Argfy. Financial Data Solutions
        </div>
      </div>
    </footer>
  )
}
