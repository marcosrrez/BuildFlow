import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { Permit, Inspection } from '../../types'
import StatusBadge from '../shared/StatusBadge'
import { PERMIT_TYPES, formatCurrency } from '../../utils/constants'
import { FileCheck, Plus, AlertTriangle, Trash2 } from 'lucide-react'

export default function PermitsPage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)

  const { data: permits } = useQuery<Permit[]>({
    queryKey: ['permits', projectId],
    queryFn: () => api.get(`/projects/${projectId}/permits`).then(r => r.data),
  })

  const { data: alerts } = useQuery({
    queryKey: ['permit-alerts', projectId],
    queryFn: () => api.get(`/projects/${projectId}/permits/alerts`).then(r => r.data),
  })

  const addPermit = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${projectId}/permits`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['permits'] }); setShowForm(false) },
  })

  const deletePermit = useMutation({
    mutationFn: (permitId: number) => api.delete(`/projects/${projectId}/permits/${permitId}`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['permits'] }); qc.invalidateQueries({ queryKey: ['permit-alerts'] }) },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Permit Tracker</h1>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus className="w-4 h-4" /> Add Permit
        </button>
      </div>

      {/* Alerts */}
      {alerts && alerts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <h3 className="font-medium text-yellow-800 flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4" /> Permit Alerts
          </h3>
          <div className="space-y-1">
            {alerts.map((a: any, i: number) => (
              <p key={i} className="text-sm text-yellow-700">{a.message}</p>
            ))}
          </div>
        </div>
      )}

      {/* Add form */}
      {showForm && (
        <form className="bg-white rounded-xl shadow-sm border p-5 space-y-4"
          onSubmit={e => {
            e.preventDefault()
            const fd = new FormData(e.currentTarget)
            addPermit.mutate({
              permit_type: fd.get('permit_type'),
              jurisdiction: fd.get('jurisdiction'),
              description: fd.get('description'),
              applicant_name: fd.get('applicant_name'),
            })
          }}>
          <h3 className="font-semibold">New Permit Application</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <select name="permit_type" required className="border rounded-lg px-3 py-2 text-sm">
              <option value="">Permit type...</option>
              {PERMIT_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
            <input name="jurisdiction" placeholder="Jurisdiction (e.g., City of...)" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="applicant_name" placeholder="Applicant name" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="description" placeholder="Description" className="border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-500 px-4 py-2 text-sm">Cancel</button>
          </div>
        </form>
      )}

      {/* Permit cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {(permits || []).map(p => (
          <div key={p.id} className="bg-white rounded-xl shadow-sm border p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-blue-500" />
                <span className="font-semibold text-gray-900 capitalize">{p.permit_type}</span>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={p.status} />
                <button
                  onClick={() => { if (window.confirm(`Delete ${p.permit_type} permit? This will also delete its inspections and fees.`)) deletePermit.mutate(p.id) }}
                  className="text-gray-400 hover:text-red-500 p-1"
                  title="Delete permit"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            {p.permit_number && <p className="text-sm text-gray-600 mb-1">#{p.permit_number}</p>}
            {p.jurisdiction && <p className="text-sm text-gray-500 mb-2">{p.jurisdiction}</p>}
            {p.description && <p className="text-sm text-gray-500 mb-2">{p.description}</p>}
            <div className="flex gap-4 text-xs text-gray-400 mt-3 pt-3 border-t">
              {p.application_date && <span>Applied: {p.application_date}</span>}
              {p.expiry_date && <span>Expires: {p.expiry_date}</span>}
            </div>
          </div>
        ))}
      </div>

      {(!permits || permits.length === 0) && !showForm && (
        <div className="text-center py-12 text-gray-500">
          <FileCheck className="w-10 h-10 mx-auto mb-3 text-gray-300" />
          <p>No permits yet. Add your first permit to start tracking.</p>
        </div>
      )}
    </div>
  )
}
