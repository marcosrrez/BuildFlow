import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import React, { useState } from 'react'
import api from '../../api/client'
import type { BudgetCategory, BudgetItem, CostSuggestion } from '../../types'
import StatCard from '../shared/StatCard'
import LearnTrigger from '../shared/LearnTrigger'
import BidLeveling from './BidLeveling'
import { formatCurrency, formatPercent, BUDGET_CATEGORIES } from '../../utils/constants'
import { DollarSign, Plus, TrendingDown, TrendingUp, Trash2, Pencil, Check, X, Sparkles, Info, ChevronDown } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function BudgetPage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [expandedItemId, setExpandedItemId] = useState<number | null>(null)
  const [editValues, setEditValues] = useState<Record<string, any>>({})
  const [formCategoryId, setFormCategoryId] = useState<number | null>(null)
  const [budgetInput, setBudgetInput] = useState<string>('')
  const [descriptionInput, setDescriptionInput] = useState<string>('')

  const toggleForm = () => {
    setShowForm(!showForm)
    setFormCategoryId(null)
    setBudgetInput('')
    setDescriptionInput('')
  }

  const { data: categories } = useQuery<BudgetCategory[]>({
    queryKey: ['budget-cats', projectId],
    queryFn: () => api.get(`/projects/${projectId}/budget/categories`).then(r => r.data),
  })

  const { data: suggestions, isLoading: suggestionsLoading } = useQuery<CostSuggestion[]>({
    queryKey: ['budget-suggestions', projectId, formCategoryId],
    queryFn: () => api.get(`/projects/${projectId}/budget/suggest?category_id=${formCategoryId}`).then(r => r.data),
    enabled: !!formCategoryId && showForm,
  })

  const { data: items } = useQuery<BudgetItem[]>({
    queryKey: ['budget-items', projectId],
    queryFn: () => api.get(`/projects/${projectId}/budget/items`).then(r => r.data),
  })

  const { data: summary } = useQuery({
    queryKey: ['budget-summary', projectId],
    queryFn: () => api.get(`/projects/${projectId}/budget/summary`).then(r => r.data),
  })

  const initCategories = useMutation({
    mutationFn: async () => {
      for (const [i, c] of BUDGET_CATEGORIES.entries()) {
        await api.post(`/projects/${projectId}/budget/categories`, { ...c, budgeted_amount: 0, sort_order: i })
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budget-cats'] })
      qc.invalidateQueries({ queryKey: ['budget-items'] })
      qc.invalidateQueries({ queryKey: ['budget-summary'] })
    },
  })

  const addItem = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${projectId}/budget/items`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budget-items'] })
      qc.invalidateQueries({ queryKey: ['budget-summary'] })
      toggleForm()
    },
  })

  const updateItem = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.put(`/projects/${projectId}/budget/items/${id}`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budget-items'] })
      qc.invalidateQueries({ queryKey: ['budget-summary'] })
      setEditingId(null)
    },
  })

  const deleteItem = useMutation({
    mutationFn: (itemId: number) => api.delete(`/projects/${projectId}/budget/items/${itemId}`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['budget-items'] }); qc.invalidateQueries({ queryKey: ['budget-summary'] }) },
  })

  const startEdit = (item: BudgetItem) => {
    setEditingId(item.id)
    setEditValues({
      description: item.description,
      current_budget: item.current_budget,
      actual_cost: item.actual_cost,
      forecast_cost: item.forecast_cost,
      percent_complete: item.percent_complete,
    })
  }

  const saveEdit = () => {
    if (editingId === null) return
    updateItem.mutate({ id: editingId, data: editValues })
  }

  const total_budget = summary?.total_budget || 0
  const total_actual = summary?.total_actual || 0
  const variance = summary?.variance || 0
  const variance_pct = summary?.variance_percent || 0

  const chartData = (summary?.categories || []).map((c: any) => ({
    name: c.name.replace(/ /g, '\n'),
    budgeted: c.budgeted,
    actual: c.actual,
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Budget Tracker</h1>
        <button onClick={toggleForm} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus className="w-4 h-4" /> Add Item
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Budget" value={formatCurrency(total_budget)} icon={<DollarSign className="w-5 h-5" />} />
        <StatCard title="Total Spent" value={formatCurrency(total_actual)} icon={<DollarSign className="w-5 h-5" />} />
        <StatCard title="Variance" value={formatCurrency(variance)}
          subtitle={formatPercent(variance_pct)}
          icon={variance >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
          status={variance_pct > -5 ? 'on_track' : variance_pct > -15 ? 'at_risk' : 'critical'} />
        <StatCard title="Committed" value={formatCurrency(summary?.total_committed || 0)} icon={<DollarSign className="w-5 h-5" />} />
      </div>

      {/* Category chart */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Budget vs Actual by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} />
              <YAxis tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: number) => formatCurrency(v)} />
              <Bar dataKey="budgeted" fill="#93c5fd" name="Budget" />
              <Bar dataKey="actual" fill="#2563eb" name="Actual" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Initialize categories button */}
      {categories && categories.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-6 text-center">
          <p className="text-gray-500 mb-3">Set up standard residential budget categories to get started.</p>
          <button
            onClick={() => initCategories.mutate()}
            disabled={initCategories.isPending}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {initCategories.isPending ? 'Creating Categories...' : 'Initialize Budget Categories'}
          </button>
        </div>
      )}

      {/* Categories list - show when categories exist but no line items yet */}
      {categories && categories.length > 0 && (!items || items.length === 0) && !showForm && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Budget Categories</h2>
          <p className="text-sm text-gray-500 mb-4">Categories are set up. Click "Add Item" above to add budget line items under each category.</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {categories.map(c => (
              <div key={c.id} className="bg-gray-50 rounded-lg px-3 py-2 text-sm">
                <span className="font-mono text-xs text-gray-400">{c.code}</span>
                <p className="text-gray-700">
                  <LearnTrigger term={c.code} mode="text" className="font-medium text-gray-900">
                    {c.name}
                  </LearnTrigger>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add item form */}
      {showForm && categories && categories.length > 0 && (
        <form
          className="bg-white rounded-xl shadow-sm border p-5 space-y-4"
          onSubmit={e => {
            e.preventDefault()
            addItem.mutate({
              category_id: Number(formCategoryId),
              item_code: new FormData(e.currentTarget).get('item_code'),
              description: descriptionInput,
              original_budget: Number(budgetInput),
              current_budget: Number(budgetInput),
            })
          }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Add Budget Item</h3>
            {suggestionsLoading && <span className="text-xs text-gray-400 animate-pulse">Fetching suggestions...</span>}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <select 
              name="category_id" 
              required 
              className="border rounded-lg px-3 py-2 text-sm"
              onChange={e => setFormCategoryId(Number(e.target.value))}
            >
              <option value="">Category...</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <input name="item_code" placeholder="Item code" required className="border rounded-lg px-3 py-2 text-sm" />
            <input 
              name="description" 
              placeholder="Description" 
              required 
              value={descriptionInput}
              onChange={e => setDescriptionInput(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm" 
            />
            <div className="relative">
              <input 
                name="original_budget" 
                type="number" 
                step="0.01" 
                placeholder="Budget amount" 
                required 
                value={budgetInput}
                onChange={e => setBudgetInput(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm" 
              />
            </div>
          </div>

          {suggestions && suggestions.length > 0 && (
            <div className="space-y-4 bg-blue-50/50 rounded-xl p-4 border border-blue-100">
              <div className="flex items-center gap-1.5 text-xs font-bold text-blue-800 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                Smart Recommendations
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Amount Suggestions */}
                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-gray-400 uppercase">Suggested Amounts</p>
                  <div className="flex flex-wrap gap-2">
                    {suggestions.map((s, idx) => (
                      <div key={idx} className="group relative">
                        <button
                          type="button"
                          onClick={() => setBudgetInput(s.amount.toString())}
                          className="flex items-center gap-2 bg-white border border-blue-200 hover:border-blue-400 hover:shadow-sm transition-all rounded-lg px-3 py-1.5 text-left"
                        >
                          <div>
                            <span className="block text-[10px] uppercase tracking-wider text-gray-400 font-bold">{s.label}</span>
                            <span className="text-sm font-semibold text-blue-600">{formatCurrency(s.amount)}</span>
                          </div>
                          <div className="text-gray-300 group-hover:text-blue-400 transition-colors">
                            <Info className="w-3.5 h-3.5" />
                          </div>
                        </button>
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-gray-900 text-white text-[10px] rounded shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                          {s.rationale}
                          <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-gray-900"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Description Suggestions */}
                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-gray-400 uppercase">Suggested Descriptions</p>
                  <div className="flex flex-wrap gap-2">
                    {suggestions[0].description_options.map((desc, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setDescriptionInput(desc)}
                        className="text-[11px] bg-white border border-gray-200 hover:border-blue-300 rounded-md px-2 py-1 text-gray-600 hover:text-blue-600 transition-colors"
                      >
                        {desc}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-500 px-4 py-2 text-sm">Cancel</button>
          </div>
        </form>
      )}

      {/* Items table */}
      {items && items.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="text-left px-4 py-3 font-medium">Code</th>
                  <th className="text-left px-4 py-3 font-medium">Description</th>
                  <th className="text-right px-4 py-3 font-medium">Budget</th>
                  <th className="text-right px-4 py-3 font-medium">Actual</th>
                  <th className="text-right px-4 py-3 font-medium">Forecast</th>
                  <th className="text-right px-4 py-3 font-medium">Variance</th>
                  <th className="text-right px-4 py-3 font-medium">% Done</th>
                  <th className="px-4 py-3 font-medium w-24"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {items.map(item => {
                  const isEditing = editingId === item.id
                  const isExpanded = expandedItemId === item.id
                  const v = item.current_budget - item.actual_cost
                  const vClass = v >= 0 ? 'text-green-600' : 'text-red-600'

                  if (isEditing) {
                    return (
                      <tr key={item.id} className="bg-blue-50">
                        <td className="px-4 py-2 font-mono text-xs">{item.item_code}</td>
                        <td className="px-4 py-2">
                          <input
                            value={editValues.description}
                            onChange={e => setEditValues({ ...editValues, description: e.target.value })}
                            className="w-full border rounded px-2 py-1 text-sm"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <input
                            type="number" step="0.01"
                            value={editValues.current_budget}
                            onChange={e => setEditValues({ ...editValues, current_budget: Number(e.target.value) })}
                            className="w-full border rounded px-2 py-1 text-sm text-right"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <input
                            type="number" step="0.01"
                            value={editValues.actual_cost}
                            onChange={e => setEditValues({ ...editValues, actual_cost: Number(e.target.value) })}
                            className="w-full border rounded px-2 py-1 text-sm text-right"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <input
                            type="number" step="0.01"
                            value={editValues.forecast_cost}
                            onChange={e => setEditValues({ ...editValues, forecast_cost: Number(e.target.value) })}
                            className="w-full border rounded px-2 py-1 text-sm text-right"
                          />
                        </td>
                        <td className="px-4 py-2 text-right text-gray-400 text-xs">auto</td>
                        <td className="px-4 py-2">
                          <input
                            type="number" step="1" min="0" max="100"
                            value={editValues.percent_complete}
                            onChange={e => setEditValues({ ...editValues, percent_complete: Number(e.target.value) })}
                            className="w-full border rounded px-2 py-1 text-sm text-right"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <div className="flex gap-1 justify-center">
                            <button onClick={saveEdit} className="text-green-600 hover:text-green-800 p-1" title="Save">
                              <Check className="w-4 h-4" />
                            </button>
                            <button onClick={() => setEditingId(null)} className="text-gray-400 hover:text-gray-600 p-1" title="Cancel">
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  }

                  return (
                    <React.Fragment key={item.id}>
                      <tr className={`hover:bg-gray-50 transition-colors ${isExpanded ? 'bg-blue-50/30' : ''}`}>
                        <td className="px-4 py-3 font-mono text-xs">{item.item_code}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {item.description}
                            <button 
                              onClick={() => setExpandedItemId(isExpanded ? null : item.id)}
                              className={`p-1 rounded hover:bg-gray-200 transition-colors ${isExpanded ? 'text-blue-600 bg-blue-100' : 'text-gray-400'}`}
                              title="Bid Leveling"
                            >
                              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                            </button>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right">{formatCurrency(item.current_budget)}</td>
                        <td className="px-4 py-3 text-right">{formatCurrency(item.actual_cost)}</td>
                        <td className="px-4 py-3 text-right text-gray-500">{item.forecast_cost ? formatCurrency(item.forecast_cost) : '-'}</td>
                        <td className={`px-4 py-3 text-right font-medium ${vClass}`}>{formatCurrency(v)}</td>
                        <td className="px-4 py-3 text-right">{formatPercent(item.percent_complete)}</td>
                        <td className="px-4 py-3">
                          <div className="flex gap-1 justify-center">
                            <button
                              onClick={() => startEdit(item)}
                              className="text-gray-400 hover:text-blue-500 p-1"
                              title="Edit item"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => { if (window.confirm(`Delete "${item.description}"?`)) deleteItem.mutate(item.id) }}
                              className="text-gray-400 hover:text-red-500 p-1"
                              title="Delete item"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr>
                          <td colSpan={8} className="px-8 pb-6 pt-0 bg-blue-50/30">
                            <BidLeveling 
                              projectId={projectId} 
                              item={item} 
                              suggestions={suggestions} 
                            />
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
