import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { Subcontractor } from '../../types'
import StatusBadge from '../shared/StatusBadge'
import { TRADES, formatCurrency } from '../../utils/constants'
import { Users, Plus, Phone, Mail, AlertTriangle, Trash2 } from 'lucide-react'

export default function SubcontractorsPage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)

  const { data: subs } = useQuery<Subcontractor[]>({
    queryKey: ['subs', projectId],
    queryFn: () => api.get(`/projects/${projectId}/subcontractors`).then(r => r.data),
  })

  const { data: missingWaivers } = useQuery({
    queryKey: ['missing-waivers', projectId],
    queryFn: () => api.get(`/projects/${projectId}/subcontractors/missing-waivers`).then(r => r.data),
  })

  const addSub = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${projectId}/subcontractors`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['subs'] }); setShowForm(false) },
  })

  const deleteSub = useMutation({
    mutationFn: (subId: number) => api.delete(`/projects/${projectId}/subcontractors/${subId}`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['subs'] }); qc.invalidateQueries({ queryKey: ['missing-waivers'] }) },
  })

  const totalContract = (subs || []).reduce((s, sub) => s + sub.contract_amount, 0)
  const totalPaid = (subs || []).reduce((s, sub) => s + sub.total_paid, 0)
  const totalRetention = (subs || []).reduce((s, sub) => s + sub.total_retention, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Subcontractors</h1>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus className="w-4 h-4" /> Add Sub
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Total Contracted</p>
          <p className="text-xl font-bold">{formatCurrency(totalContract)}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Total Paid</p>
          <p className="text-xl font-bold">{formatCurrency(totalPaid)}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Retention Held</p>
          <p className="text-xl font-bold">{formatCurrency(totalRetention)}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Active Subs</p>
          <p className="text-xl font-bold">{(subs || []).filter(s => s.status === 'active').length}</p>
        </div>
      </div>

      {/* Missing waivers alert */}
      {missingWaivers && missingWaivers.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <h3 className="font-medium text-yellow-800 flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4" /> Missing Lien Waivers ({missingWaivers.length})
          </h3>
          {missingWaivers.map((w: any, i: number) => (
            <p key={i} className="text-sm text-yellow-700">{w.subcontractor_name} - Invoice {w.invoice_number || 'N/A'} ({formatCurrency(w.amount)})</p>
          ))}
        </div>
      )}

      {/* Add form */}
      {showForm && (
        <form className="bg-white rounded-xl shadow-sm border p-5 space-y-4"
          onSubmit={e => {
            e.preventDefault()
            const fd = new FormData(e.currentTarget)
            addSub.mutate({
              company_name: fd.get('company_name'),
              contact_name: fd.get('contact_name'),
              email: fd.get('email'),
              phone: fd.get('phone'),
              trade: fd.get('trade'),
              license_number: fd.get('license_number'),
              contract_amount: Number(fd.get('contract_amount') || 0),
              retention_percent: Number(fd.get('retention_percent') || 10) / 100,
            })
          }}>
          <h3 className="font-semibold">Add Subcontractor</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <input name="company_name" placeholder="Company name" required className="border rounded-lg px-3 py-2 text-sm" />
            <input name="contact_name" placeholder="Contact name" className="border rounded-lg px-3 py-2 text-sm" />
            <select name="trade" required className="border rounded-lg px-3 py-2 text-sm">
              <option value="">Trade...</option>
              {TRADES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <input name="phone" placeholder="Phone" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="email" placeholder="Email" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="license_number" placeholder="License #" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="contract_amount" type="number" step="0.01" placeholder="Contract amount" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="retention_percent" type="number" step="1" placeholder="Retention % (default 10)" className="border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-500 px-4 py-2 text-sm">Cancel</button>
          </div>
        </form>
      )}

      {/* Sub cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {(subs || []).map(sub => (
          <div key={sub.id} className="bg-white rounded-xl shadow-sm border p-5">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">{sub.company_name}</h3>
              <div className="flex items-center gap-2">
                <StatusBadge status={sub.status} />
                <button
                  onClick={() => { if (window.confirm(`Delete ${sub.company_name}? This will also delete all their payments and waivers.`)) deleteSub.mutate(sub.id) }}
                  className="text-gray-400 hover:text-red-500 p-1"
                  title="Delete subcontractor"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            <p className="text-sm text-gray-500 mb-1">{sub.trade}{sub.contact_name ? ` - ${sub.contact_name}` : ''}</p>
            <div className="flex gap-4 text-xs text-gray-400 mb-3">
              {sub.phone && <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> {sub.phone}</span>}
              {sub.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> {sub.email}</span>}
            </div>
            <div className="grid grid-cols-3 gap-2 text-center bg-gray-50 rounded-lg p-3">
              <div>
                <p className="text-xs text-gray-500">Contract</p>
                <p className="font-semibold text-sm">{formatCurrency(sub.contract_amount)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Paid</p>
                <p className="font-semibold text-sm">{formatCurrency(sub.total_paid)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Balance</p>
                <p className="font-semibold text-sm">{formatCurrency(sub.balance_remaining)}</p>
              </div>
            </div>
            {sub.license_number && <p className="text-xs text-gray-400 mt-2">License: {sub.license_number}</p>}
          </div>
        ))}
      </div>

      {(!subs || subs.length === 0) && !showForm && (
        <div className="text-center py-12 text-gray-500">
          <Users className="w-10 h-10 mx-auto mb-3 text-gray-300" />
          <p>No subcontractors yet. Add your first sub to start tracking.</p>
        </div>
      )}
    </div>
  )
}
