import { ReactNode } from 'react'

interface Column<T = any> {
  key: string
  header: string
  render?: (row: T) => ReactNode
  className?: string
}

interface TableProps<T = any> {
  columns: Column<T>[]
  data: T[]
  onRowClick?: (row: T) => void
  emptyMessage?: string
  loading?: boolean
}

function Table<T extends { [key: string]: any }>({
  columns,
  data,
  onRowClick,
  emptyMessage = 'No hay datos disponibles',
  loading = false,
}: TableProps<T>) {
  return (
    <div className="overflow-x-auto border border-slate-700 rounded-lg">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-800 text-slate-300 uppercase text-xs">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-4 py-3 font-medium ${col.className || ''}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                  <span>Cargando...</span>
                </div>
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr
                key={i}
                onClick={() => onRowClick?.(row)}
                className={`
                  border-t border-slate-700/50 bg-slate-900/50
                  ${onRowClick ? 'cursor-pointer hover:bg-slate-800/50' : ''}
                `}
              >
                {columns.map((col) => (
                  <td key={col.key} className={`px-4 py-3 ${col.className || ''}`}>
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export { Table }
export type { Column }
