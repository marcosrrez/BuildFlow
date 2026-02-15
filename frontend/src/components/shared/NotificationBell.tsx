import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bell, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'

interface Notification {
  id: string
  category: string
  severity: string
  title: string
  message: string
  action_url: string | null
}

interface NotificationList {
  total: number
  critical_count: number
  warning_count: number
  info_count: number
  notifications: Notification[]
}

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'border-l-red-500 bg-red-50',
  warning: 'border-l-amber-500 bg-amber-50',
  info: 'border-l-blue-500 bg-blue-50',
}

const SEVERITY_DOT: Record<string, string> = {
  critical: 'bg-red-500',
  warning: 'bg-amber-500',
  info: 'bg-blue-500',
}

export default function NotificationBell({ projectId }: { projectId: number }) {
  const [isOpen, setIsOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  const { data } = useQuery<NotificationList>({
    queryKey: ['notifications', projectId],
    queryFn: () => api.get(`/projects/${projectId}/notifications`).then(r => r.data),
    refetchInterval: 60000,
  })

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setIsOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const count = data?.total ?? 0
  const critCount = data?.critical_count ?? 0

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-400 hover:text-gray-600 transition-colors"
        title="Notifications"
      >
        <Bell className="w-5 h-5" />
        {count > 0 && (
          <span className={`absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-bold text-white rounded-full px-1 ${
            critCount > 0 ? 'bg-red-500' : 'bg-amber-500'
          }`}>
            {count > 99 ? '99+' : count}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 max-h-96 bg-white rounded-xl shadow-xl border overflow-hidden z-50">
          <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
            <span className="font-semibold text-sm text-gray-900">
              Notifications ({count})
            </span>
            <button onClick={() => setIsOpen(false)}>
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div className="overflow-y-auto max-h-[320px]">
            {!data || data.notifications.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-6">
                No notifications
              </p>
            ) : (
              data.notifications.map((n) => (
                <button
                  key={n.id}
                  onClick={() => {
                    if (n.action_url) navigate(n.action_url)
                    setIsOpen(false)
                  }}
                  className={`w-full text-left px-4 py-3 border-b border-l-4 hover:bg-gray-50 transition-colors ${
                    SEVERITY_STYLES[n.severity] || ''
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                      SEVERITY_DOT[n.severity] || 'bg-gray-400'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{n.title}</p>
                      <p className="text-xs text-gray-600 mt-0.5">{n.message}</p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
