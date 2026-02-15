import { ReactNode } from 'react'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  icon?: ReactNode
  status?: 'on_track' | 'at_risk' | 'critical'
}

const ring: Record<string, string> = {
  on_track: 'border-l-green-500',
  at_risk: 'border-l-yellow-500',
  critical: 'border-l-red-500',
}

export default function StatCard({ title, value, subtitle, icon, status }: Props) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-5 border-l-4 ${status ? ring[status] : 'border-l-blue-500'}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        {icon && <span className="text-gray-400">{icon}</span>}
      </div>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
    </div>
  )
}
