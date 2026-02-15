import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { Bid, BudgetItem, CostSuggestion } from '../../types'
import { formatCurrency } from '../../utils/constants'
import { Plus, Trash2, CheckCircle, Info, TrendingDown, TrendingUp, AlertCircle } from 'lucide-react'
import LearnTrigger from '../shared/LearnTrigger'

interface BidLevelingProps {
  projectId: number
  item: BudgetItem
  suggestions?: CostSuggestion[]
}

export default function BidLeveling({ projectId, item, suggestions }: BidLevelingProps) {
  const qc = useQueryClient()
  const [showAddBid, setShowAddBid] = useState(false)

  const { data: bids, isLoading } = useQuery<Bid[]>({
    queryKey: ['bids', projectId, item.id],
    queryFn: () => api.get(`/projects/${projectId}/budget/items/${item.id}/bids`).then(r => r.data),
  })

  const addBid = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${projectId}/budget/items/${item.id}/bids`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['bids', projectId, item.id] })
      setShowAddBid(false)
    },
  })

  const selectBid = useMutation({
    mutationFn: (bidId: number) => api.put(`/projects/${projectId}/budget/bids/${bidId}`, { is_selected: true }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['bids', projectId, item.id] })
      qc.invalidateQueries({ queryKey: ['budget-items'] })
      qc.invalidateQueries({ queryKey: ['budget-summary'] })
    },
  })

  const deleteBid = useMutation({
    mutationFn: (bidId: number) => api.delete(`/projects/${projectId}/budget/bids/${bidId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bids', projectId, item.id] }),
  })

  const avgSuggestion = suggestions?.find(s => s.type === 'average')?.amount || item.current_budget

  return (
    <div className="bg-gray-50/50 rounded-xl border p-4 mt-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h4 className="font-bold text-gray-900 text-sm uppercase tracking-tight">Bid Leveling</h4>
          <LearnTrigger term="Bid packages" mode="icon" />
        </div>
        <button 
          onClick={() => setShowAddBid(true)}
          className="text-xs flex items-center gap-1 bg-white border shadow-sm px-2 py-1 rounded hover:bg-gray-50 transition-colors"
        >
          <Plus className="w-3 h-3" /> Add Bid
        </button>
      </div>

      {isLoading ? (
        <div className="h-20 animate-pulse bg-gray-100 rounded-lg" />
      ) : bids && bids.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-gray-400 border-b">
                <th className="text-left py-2 font-bold uppercase tracking-wider">Contractor</th>
                <th className="text-right py-2 font-bold uppercase tracking-wider">Amount</th>
                <th className="text-right py-2 font-bold uppercase tracking-wider">Variance</th>
                <th className="text-center py-2 font-bold uppercase tracking-wider">Status</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {bids.map(bid => {
                const variance = bid.amount - avgSuggestion
                const variancePct = (variance / avgSuggestion) * 100
                
                return (
                  <tr key={bid.id} className={`${bid.is_selected ? 'bg-blue-50/50' : ''}`}>
                    <td className="py-3 font-semibold text-gray-700">{bid.contractor_name}</td>
                    <td className="py-3 text-right font-mono font-medium">{formatCurrency(bid.amount)}</td>
                    <td className="py-3 text-right font-mono">
                      <div className={`flex items-center justify-end gap-1 ${variance <= 0 ? 'text-green-600' : 'text-amber-600'}`}>
                        {variance <= 0 ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
                        {formatCurrency(Math.abs(variance))}
                        <span className="text-[10px] opacity-70">({variancePct.toFixed(0)}%)</span>
                      </div>
                    </td>
                    <td className="py-3 text-center">
                      {bid.is_selected ? (
                        <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold uppercase text-[9px]">
                          Selected
                        </span>
                      ) : (
                        <button 
                          onClick={() => selectBid.mutate(bid.id)}
                          className="text-gray-400 hover:text-blue-600 transition-colors"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                    <td className="py-3 text-right">
                      <button 
                        onClick={() => { if(confirm('Delete this bid?')) deleteBid.mutate(bid.id) }}
                        className="text-gray-300 hover:text-red-500"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          
          {/* Analysis Note */}
          <div className="mt-4 flex gap-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
            <Info className="w-4 h-4 text-blue-500 shrink-0" />
            <p className="text-[11px] text-blue-800 leading-relaxed">
              <strong>Leveling Tip:</strong> Compare bids not just on total price, but on what's included. 
              {bids.length > 1 && bids.some(b => b.amount < avgSuggestion * 0.8) && (
                <span className="block mt-1 font-bold">
                  <AlertCircle className="inline w-3 h-3 mr-1" />
                  Warning: One or more bids are significantly below average. Check for missing scope items!
                </span>
              )}
            </p>
          </div>
        </div>
      ) : (
        <div className="text-center py-6 border-2 border-dashed rounded-lg bg-white">
          <p className="text-xs text-gray-400">No bids added yet. Compare multiple quotes to level your costs.</p>
        </div>
      )}

      {showAddBid && (
        <form 
          className="bg-white p-4 rounded-lg border shadow-sm space-y-3"
          onSubmit={e => {
            e.preventDefault()
            const fd = new FormData(e.currentTarget)
            addBid.mutate({
              contractor_name: fd.get('contractor_name'),
              amount: Number(fd.get('amount')),
              notes: fd.get('notes')
            })
          }}
        >
          <div className="grid grid-cols-2 gap-3">
            <input name="contractor_name" placeholder="Contractor name" required className="border rounded px-2 py-1.5 text-xs" />
            <input name="amount" type="number" step="0.01" placeholder="Bid amount" required className="border rounded px-2 py-1.5 text-xs" />
          </div>
          <textarea name="notes" placeholder="Notes (exclusions, inclusions...)" className="w-full border rounded px-2 py-1.5 text-xs h-16" />
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded text-xs font-medium">Save Bid</button>
            <button type="button" onClick={() => setShowAddBid(false)} className="text-gray-400 text-xs">Cancel</button>
          </div>
        </form>
      )}
    </div>
  )
}
