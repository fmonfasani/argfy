import Link from "next/link"

export default function ApiPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold mb-4">API</h1>
        <p className="text-slate-400 text-lg mb-12">
          Acceso programático a datos fundamentales de CEDEARs y métricas financieras.
        </p>

        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Endpoints</h2>
            <div className="bg-slate-900 rounded-lg p-6 space-y-4 font-mono text-sm">
              <div>
                <span className="text-green-400">GET</span>{" "}
                <span className="text-slate-300">/api/v1/fundamentals/screener</span>
                <p className="text-slate-500 mt-1 font-sans text-xs">Lista de CEDEARs con filtros y ordenamiento</p>
              </div>
              <div>
                <span className="text-green-400">GET</span>{" "}
                <span className="text-slate-300">/api/v1/fundamentals/{`<ticker>`}</span>
                <p className="text-slate-500 mt-1 font-sans text-xs">Detalle fundamental de un ticker</p>
              </div>
              <div>
                <span className="text-green-400">GET</span>{" "}
                <span className="text-slate-300">/api/v1/fundamentals/{`<ticker>`}/price</span>
                <p className="text-slate-500 mt-1 font-sans text-xs">Historial de precios</p>
              </div>
              <div>
                <span className="text-green-400">GET</span>{" "}
                <span className="text-slate-300">/api/v1/fundamentals/{`<ticker>`}/history</span>
                <p className="text-slate-500 mt-1 font-sans text-xs">Historial de métricas trimestrales</p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Planes</h2>
            <p className="text-slate-400 mb-4">
              El acceso a la API está disponible en los planes Pro y Enterprise.
            </p>
            <Link
              href="/pricing"
              className="text-amber-400 hover:text-amber-300 font-semibold transition-colors"
            >
              Ver planes y precios &rarr;
            </Link>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Documentación</h2>
            <p className="text-slate-400 mb-4">
              La documentación interactiva de la API está disponible en:
            </p>
            <code className="bg-slate-900 px-3 py-1 rounded text-amber-400">
              {process.env.NEXT_PUBLIC_API_BASE}/docs
            </code>
          </section>
        </div>
      </div>
    </div>
  )
}
