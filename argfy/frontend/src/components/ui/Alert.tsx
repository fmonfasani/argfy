import { ReactNode } from 'react'

const VARIANTS = {
  info: {
    bg: 'bg-blue-900/30',
    border: 'border-blue-500',
    icon: 'ℹ️',
    text: 'text-blue-200',
  },
  success: {
    bg: 'bg-emerald-900/30',
    border: 'border-emerald-500',
    icon: '✅',
    text: 'text-emerald-200',
  },
  warning: {
    bg: 'bg-amber-900/30',
    border: 'border-amber-500',
    icon: '⚠️',
    text: 'text-amber-200',
  },
  error: {
    bg: 'bg-red-900/30',
    border: 'border-red-500',
    icon: '❌',
    text: 'text-red-200',
  },
}

interface AlertProps {
  variant?: keyof typeof VARIANTS
  title?: string
  children: ReactNode
  onClose?: () => void
}

function Alert({ variant = 'info', title, children, onClose }: AlertProps) {
  const style = VARIANTS[variant]

  return (
    <div className={`flex gap-3 p-4 rounded-lg border ${style.bg} ${style.border}`}>
      <span className="text-lg flex-shrink-0">{style.icon}</span>
      <div className="flex-1 min-w-0">
        {title && <p className={`font-semibold ${style.text} text-sm`}>{title}</p>}
        <div className={`text-sm mt-1 ${style.text}`}>{children}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className={`text-slate-400 hover:text-white flex-shrink-0 ${style.text}`}
        >
          ✕
        </button>
      )}
    </div>
  )
}

export { Alert }
