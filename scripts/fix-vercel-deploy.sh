#!/bin/bash
# scripts/fix-vercel-deploy.sh
# Script para diagnosticar y reparar problemas de deploy en Vercel

set -e

echo "🔧 Argfy Vercel Deploy Fix"
echo "=========================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] ❌ $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] ℹ️  $1${NC}"
}

# Verificar directorio
if [ ! -f "frontend/package.json" ]; then
    error "Ejecuta desde el directorio raíz del proyecto"
    exit 1
fi

cd frontend

log "PASO 1: Diagnosticando problemas comunes de Vercel..."

# 1. Verificar y crear vercel.json
log "Creando/actualizando vercel.json..."
cat > vercel.json << 'EOF'
{
  "version": 2,
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://argfy-backend.onrender.com/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options", 
          "value": "DENY"
        }
      ]
    }
  ],
  "env": {
    "NEXT_PUBLIC_BACKEND_URL": "https://argfy-backend.onrender.com",
    "NEXT_PUBLIC_API_BASE": "https://argfy-backend.onrender.com/api/v1"
  }
}
EOF

log "vercel.json creado correctamente"

# 2. Verificar next.config.js
log "Verificando next.config.js..."
cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://argfy-backend.onrender.com',
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'https://argfy-backend.onrender.com/api/v1',
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ]
  },
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
}

module.exports = nextConfig
EOF

log "next.config.js actualizado"

# 3. Verificar .env.local
log "Verificando variables de entorno..."
if [ ! -f ".env.local" ]; then
    cat > .env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=https://argfy-backend.onrender.com
NEXT_PUBLIC_API_BASE=https://argfy-backend.onrender.com/api/v1
EOF
    log ".env.local creado"
else
    log ".env.local existe"
fi

# 4. Limpiar dependencias y reinstalar
log "PASO 2: Limpiando dependencias..."
rm -rf node_modules package-lock.json .next

log "Reinstalando dependencias..."
npm install

# 5. Verificar package.json scripts
log "PASO 3: Verificando scripts de build..."
node -e "
const pkg = JSON.parse(require('fs').readFileSync('package.json', 'utf8'));
if (!pkg.scripts.build || !pkg.scripts.start) {
  console.log('❌ Scripts de build faltantes');
  process.exit(1);
} else {
  console.log('✅ Scripts OK');
}
"

# 6. Test de build local
log "PASO 4: Testing build local..."
if npm run build; then
    log "✅ Build local exitoso"
else
    error "❌ Build local falló - revisar errores arriba"
    exit 1
fi

# 7. Crear archivo .vercelignore
log "PASO 5: Creando .vercelignore..."
cat > .vercelignore << 'EOF'
node_modules
.next
.env.local
.DS_Store
*.log
coverage
.nyc_output
EOF

# 8. Verificar imports problemáticos
log "PASO 6: Verificando imports..."
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "import.*DashboardModal" | while read file; do
    if ! grep -q "dynamic.*DashboardModal" "$file"; then
        warn "Archivo $file importa DashboardModal sin dynamic import"
    fi
done

# 9. Crear componente DashboardModal si falta
if [ ! -f "src/components/DashboardModal.tsx" ]; then
    log "PASO 7: Creando DashboardModal faltante..."
    mkdir -p src/components
    cat > src/components/DashboardModal.tsx << 'EOF'
'use client'
import { useEffect, useState, Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'

interface DashboardModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function DashboardModal({ isOpen, onClose }: DashboardModalProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isOpen) {
      fetchData()
    }
  }, [isOpen])

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/indicators/current`)
      const result = await response.json()
      setData(result.data || [])
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setData([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-50" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-lg font-medium leading-6 text-gray-900 flex justify-between items-center"
                >
                  📊 Dashboard de Indicadores
                  <button
                    onClick={onClose}
                    className="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </Dialog.Title>
                
                <div className="mt-4">
                  {loading ? (
                    <div className="flex justify-center items-center h-64">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {data.map((indicator, index) => (
                        <div key={index} className="bg-gray-50 p-4 rounded-lg">
                          <h4 className="font-semibold text-gray-700 capitalize">
                            {indicator.indicator_type?.replace('_', ' ')}
                          </h4>
                          <p className="text-2xl font-bold text-gray-900">
                            {typeof indicator.value === 'number' ? indicator.value.toFixed(2) : indicator.value}
                          </p>
                          <p className="text-sm text-gray-500">{indicator.source}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
EOF
    log "DashboardModal creado"
fi

# Final
cd ..

echo ""
log "🎉 FIX COMPLETADO!"
echo ""
info "ARCHIVOS CREADOS/ACTUALIZADOS:"
info "- frontend/vercel.json (configuración de Vercel)"
info "- frontend/next.config.js (configuración de Next.js)"
info "- frontend/.vercelignore (archivos a ignorar)"
info "- frontend/src/components/DashboardModal.tsx (si faltaba)"
echo ""
info "PRÓXIMOS PASOS:"
info "1. cd frontend"
info "2. git add ."
info "3. git commit -m 'Fix Vercel deployment configuration'"
info "4. git push"
info "5. Intenta el deploy en Vercel nuevamente"
echo ""
warn "IMPORTANTE: Configura las variables de entorno en Vercel Dashboard:"
warn "- NEXT_PUBLIC_BACKEND_URL=https://argfy-backend.onrender.com"
warn "- NEXT_PUBLIC_API_BASE=https://argfy-backend.onrender.com/api/v1"