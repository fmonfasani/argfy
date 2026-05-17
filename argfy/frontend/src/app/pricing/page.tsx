"use client"
import Link from "next/link"

const plans = [
  {
    name: "Free",
    price: "$0",
    desc: "Para inversores minoristas",
    features: [
      "415 empresas con datos fundamentales",
      "5 filtros en el screener",
      "Precio actual y ratios básicos",
      "Sin historial de precios",
      "Sin API access",
    ],
    cta: "Empezar gratis",
    href: "/auth/register",
    featured: false,
  },
  {
    name: "Pro",
    price: "$999",
    period: "/mes",
    desc: "Para traders activos y analistas",
    features: [
      "Todo Free +",
      "Filtros ilimitados",
      "Historial de precios 5y",
      "Historial de métricas trimestral",
      "API access (60 req/min)",
      "Export CSV avanzado",
    ],
    cta: "Suscribirse",
    href: "#",
    featured: true,
  },
  {
    name: "Enterprise",
    price: "A medida",
    desc: "Para instituciones y developers",
    features: [
      "Todo Pro +",
      "API access (300 req/min)",
      "Soporte prioritario",
      "Slack channel dedicado",
      "Onboarding asistido",
      "SLA 99.9%",
    ],
    cta: "Contactar",
    href: "#",
    featured: false,
  },
]

export default function PricingPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4">Planes</h1>
        <p className="text-xl text-slate-400">Elegí el plan que mejor se adapte a tus necesidades</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`rounded-2xl p-8 ${
              plan.featured
                ? "bg-amber-900/20 border-2 border-amber-500 relative"
                : "bg-slate-800/50 border border-slate-700"
            }`}
          >
            {plan.featured && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-amber-500 text-slate-900 px-4 py-1 rounded-full text-sm font-semibold">
                Más popular
              </div>
            )}
            <h2 className="text-2xl font-bold text-white mb-1">{plan.name}</h2>
            <p className="text-slate-400 text-sm mb-4">{plan.desc}</p>
            <div className="mb-6">
              <span className="text-4xl font-bold text-white">{plan.price}</span>
              {plan.period && <span className="text-slate-400 ml-1">{plan.period}</span>}
            </div>

            <ul className="space-y-3 mb-8">
              {plan.features.map((f) => (
                <li key={f} className="text-slate-300 text-sm flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✓</span>
                  {f}
                </li>
              ))}
            </ul>

            <Link
              href={plan.href}
              className={`block text-center py-3 rounded-lg font-semibold transition-colors ${
                plan.featured
                  ? "bg-amber-600 text-slate-900 hover:bg-amber-500"
                  : "bg-slate-700 text-white hover:bg-slate-600"
              }`}
            >
              {plan.cta}
            </Link>
          </div>
        ))}
      </div>

      <div className="mt-12 text-center text-sm text-slate-500 max-w-2xl mx-auto">
        La información provista no constituye asesoramiento financiero ni recomendación de inversión.
        Consulte a un agente registrado ante la CNV.
      </div>
    </div>
  )
}
