import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { PunchItem } from '../../types'
import StatusBadge from '../shared/StatusBadge'
import { TRADES, PRIORITIES } from '../../utils/constants'
import { ClipboardCheck, Plus, Camera, Filter, Trash2 } from 'lucide-react'

export default function PunchListPage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [filterTrade, setFilterTrade] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  const params = new URLSearchParams()
  if (filterTrade) params.set('trade', filterTrade)
  if (filterStatus) params.set('status', filterStatus)

  const { data: items } = useQuery<PunchItem[]>({
    queryKey: ['punch-items', projectId, filterTrade, filterStatus],
    queryFn: () => api.get(`/projects/${projectId}/punchlist/items?${params}`).then(r => r.data),
  })

  const { data: stats } = useQuery({
    queryKey: ['punch-stats', projectId],
    queryFn: () => api.get(`/projects/${projectId}/punchlist/statistics`).then(r => r.data),
  })

  const createList = useMutation({
    mutationFn: () => api.post(`/projects/${projectId}/punchlist/lists`, { name: 'Main Punch List' }),
  })

  const addItem = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${projectId}/punchlist/items`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['punch-items'] }); qc.invalidateQueries({ queryKey: ['punch-stats'] }); setShowForm(false) },
  })

  const completeItem = useMutation({
    mutationFn: (id: number) => api.post(`/projects/${projectId}/punchlist/items/${id}/complete`, { completed_by: 'Owner' }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['punch-items'] }); qc.invalidateQueries({ queryKey: ['punch-stats'] }) },
  })

  const deleteItem = useMutation({
    mutationFn: (id: number) => api.delete(`/projects/${projectId}/punchlist/items/${id}`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['punch-items'] }); qc.invalidateQueries({ queryKey: ['punch-stats'] }) },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Punch List</h1>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus className="w-4 h-4" /> Add Item
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-lg border p-3 text-center">
            <p className="text-2xl font-bold">{stats.total}</p><p className="text-xs text-gray-500">Total</p>
          </div>
          <div className="bg-blue-50 rounded-lg border border-blue-200 p-3 text-center">
            <p className="text-2xl font-bold text-blue-700">{stats.open}</p><p className="text-xs text-blue-600">Open</p>
          </div>
          <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3 text-center">
            <p className="text-2xl font-bold text-yellow-700">{stats.in_progress}</p><p className="text-xs text-yellow-600">In Progress</p>
          </div>
          <div className="bg-green-50 rounded-lg border border-green-200 p-3 text-center">
            <p className="text-2xl font-bold text-green-700">{stats.verified}</p><p className="text-xs text-green-600">Verified</p>
          </div>
          <div className="bg-red-50 rounded-lg border border-red-200 p-3 text-center">
            <p className="text-2xl font-bold text-red-700">{stats.overdue}</p><p className="text-xs text-red-600">Overdue</p>
          </div>
          <div className="bg-white rounded-lg border p-3 text-center">
            <p className="text-2xl font-bold">{stats.completion_rate}%</p><p className="text-xs text-gray-500">Done</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 items-center flex-wrap">
        <Filter className="w-4 h-4 text-gray-400" />
        <select value={filterTrade} onChange={e => setFilterTrade(e.target.value)} className="border rounded-lg px-3 py-1.5 text-sm">
          <option value="">All Trades</option>
          {TRADES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="border rounded-lg px-3 py-1.5 text-sm">
          <option value="">All Statuses</option>
          {['Open', 'Assigned', 'In Progress', 'Completed', 'Verified', 'Rejected'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* Add form */}
      {showForm && (
        <form className="bg-white rounded-xl shadow-sm border p-5 space-y-4"
          onSubmit={async e => {
            e.preventDefault()
            const fd = new FormData(e.currentTarget)
            // Ensure a punch list exists
            let listId: number
            try {
              const lists = await api.get(`/projects/${projectId}/punchlist/lists`).then(r => r.data)
              if (lists.length === 0) {
                const res = await createList.mutateAsync()
                listId = res.data.id
              } else {
                listId = lists[0].id
              }
            } catch { return }
            addItem.mutate({
              punch_list_id: listId,
              description: fd.get('description'),
              location: fd.get('location'),
              trade: fd.get('trade'),
              priority: fd.get('priority'),
              assigned_to: fd.get('assigned_to') || undefined,
            })
          }}>
          <h3 className="font-semibold flex items-center gap-2"><Camera className="w-4 h-4" /> New Punch Item</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <textarea name="description" placeholder="Describe the issue..." required rows={2} className="border rounded-lg px-3 py-2 text-sm sm:col-span-2" />
            <input name="location" placeholder="Location (e.g., Master Bath)" required className="border rounded-lg px-3 py-2 text-sm" />
            <select name="trade" required className="border rounded-lg px-3 py-2 text-sm">
              <option value="">Trade...</option>
              {TRADES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <select name="priority" className="border rounded-lg px-3 py-2 text-sm">
              {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
            <input name="assigned_to" placeholder="Assigned to (optional)" className="border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-500 px-4 py-2 text-sm">Cancel</button>
          </div>
        </form>
      )}

      {/* Items */}
      <div className="space-y-3">
        {(items || []).map(item => (
          <div key={item.id} className="bg-white rounded-xl shadow-sm border p-4 flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <StatusBadge status={item.status} />
                <StatusBadge status={item.priority} />
                <span className="text-xs text-gray-400">{item.trade}</span>
              </div>
              <p className="text-sm text-gray-800">{item.description}</p>
              <p className="text-xs text-gray-500 mt-1">{item.location}{item.assigned_to ? ` | ${item.assigned_to}` : ''}</p>
            </div>
            <div className="flex gap-2">
              {item.status !== 'Verified' && item.status !== 'Completed' && (
                <button
                  onClick={() => completeItem.mutate(item.id)}
                  className="text-green-600 border border-green-300 rounded-lg px-3 py-1.5 text-xs hover:bg-green-50 whitespace-nowrap"
                >
                  Mark Done
                </button>
              )}
              <button
                onClick={() => { if (window.confirm('Delete this punch item?')) deleteItem.mutate(item.id) }}
                className="text-gray-400 hover:text-red-500 p-1.5"
                title="Delete item"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {(!items || items.length === 0) && !showForm && (
        <div className="text-center py-12 text-gray-500">
          <ClipboardCheck className="w-10 h-10 mx-auto mb-3 text-gray-300" />
          <p>No punch items yet. Add your first item to start tracking.</p>
        </div>
      )}
    </div>
  )
}
