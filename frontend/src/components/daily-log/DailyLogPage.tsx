import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { DailyLog } from '../../types'
import StatusBadge from '../shared/StatusBadge'
import { TRADES } from '../../utils/constants'
import { BookOpen, Plus, CloudSun, Trash2 } from 'lucide-react'

export default function DailyLogPage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)

  const { data: logs } = useQuery<DailyLog[]>({
    queryKey: ['daily-logs', projectId],
    queryFn: () => api.get(`/projects/${projectId}/daily-logs`).then(r => r.data),
  })

  const addLog = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${projectId}/daily-logs`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['daily-logs'] }); setShowForm(false) },
  })

  const deleteLog = useMutation({
    mutationFn: (logId: number) => api.delete(`/projects/${projectId}/daily-logs/${logId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['daily-logs'] }),
  })

  const today = new Date().toISOString().split('T')[0]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Daily Log</h1>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus className="w-4 h-4" /> New Entry
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <form className="bg-white rounded-xl shadow-sm border p-5 space-y-5"
          onSubmit={e => {
            e.preventDefault()
            const fd = new FormData(e.currentTarget)
            const crewTrade = fd.get('crew_trade') as string
            addLog.mutate({
              log_date: fd.get('log_date') || today,
              weather_condition: fd.get('weather_condition'),
              weather_temp: fd.get('weather_temp') ? Number(fd.get('weather_temp')) : undefined,
              weather_impact: fd.get('weather_impact') || 'none',
              work_summary: fd.get('work_summary'),
              work_planned: fd.get('work_planned'),
              issues: fd.get('issues'),
              safety_notes: fd.get('safety_notes'),
              prepared_by: fd.get('prepared_by'),
              crew_entries: crewTrade ? [{
                trade: crewTrade,
                company_name: fd.get('crew_company'),
                headcount: Number(fd.get('crew_headcount') || 0),
                hours_worked: Number(fd.get('crew_hours') || 0),
              }] : [],
              work_items: fd.get('work_desc') ? [{
                trade: fd.get('work_trade'),
                description: fd.get('work_desc'),
                status: fd.get('work_status') || 'completed',
              }] : [],
            })
          }}>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Date</label>
              <input name="log_date" type="date" defaultValue={today} className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Prepared By</label>
              <input name="prepared_by" placeholder="Your name" className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Weather Impact</label>
              <select name="weather_impact" className="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="none">None</option><option value="minor">Minor</option>
                <option value="major">Major</option><option value="shutdown">Shutdown</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Weather Condition</label>
              <input name="weather_condition" placeholder="e.g., Sunny, 75F" className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Temperature (F)</label>
              <input name="weather_temp" type="number" placeholder="75" className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>

          <fieldset className="border rounded-lg p-3">
            <legend className="text-xs font-medium text-gray-600 px-1">Crew On Site</legend>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <select name="crew_trade" className="border rounded-lg px-2 py-1.5 text-sm">
                <option value="">Trade</option>
                {TRADES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <input name="crew_company" placeholder="Company" className="border rounded-lg px-2 py-1.5 text-sm" />
              <input name="crew_headcount" type="number" placeholder="# Workers" className="border rounded-lg px-2 py-1.5 text-sm" />
              <input name="crew_hours" type="number" step="0.5" placeholder="Hours" className="border rounded-lg px-2 py-1.5 text-sm" />
            </div>
          </fieldset>

          <fieldset className="border rounded-lg p-3">
            <legend className="text-xs font-medium text-gray-600 px-1">Work Completed</legend>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <select name="work_trade" className="border rounded-lg px-2 py-1.5 text-sm">
                <option value="">Trade</option>
                {TRADES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <input name="work_desc" placeholder="Description of work" className="border rounded-lg px-2 py-1.5 text-sm" />
              <select name="work_status" className="border rounded-lg px-2 py-1.5 text-sm">
                <option value="completed">Completed</option>
                <option value="partial">Partial</option>
                <option value="delayed">Delayed</option>
              </select>
            </div>
          </fieldset>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Work Summary</label>
            <textarea name="work_summary" rows={2} placeholder="Summary of today's work..." className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Issues / Notes</label>
            <textarea name="issues" rows={2} placeholder="Any issues or notes..." className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Safety Notes</label>
            <textarea name="safety_notes" rows={1} placeholder="Safety observations..." className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>

          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Save Log</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-500 px-4 py-2 text-sm">Cancel</button>
          </div>
        </form>
      )}

      {/* Log list */}
      <div className="space-y-3">
        {(logs || []).map(log => (
          <div key={log.id} className="bg-white rounded-xl shadow-sm border p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-gray-900">{new Date(log.log_date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</span>
                {log.weather_condition && (
                  <span className="flex items-center gap-1 text-sm text-gray-500">
                    <CloudSun className="w-4 h-4" /> {log.weather_condition} {log.weather_temp ? `${log.weather_temp}F` : ''}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {log.weather_impact && log.weather_impact !== 'none' && (
                  <StatusBadge status={log.weather_impact} />
                )}
                <button
                  onClick={() => { if (window.confirm('Delete this daily log entry?')) deleteLog.mutate(log.id) }}
                  className="text-gray-400 hover:text-red-500 p-1"
                  title="Delete log"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            {log.work_summary && <p className="text-sm text-gray-700 mb-1">{log.work_summary}</p>}
            {log.issues && <p className="text-sm text-red-600">Issues: {log.issues}</p>}
            {log.crew_entries && log.crew_entries.length > 0 && (
              <div className="mt-2 flex gap-2 flex-wrap">
                {log.crew_entries.map((c, i) => (
                  <span key={i} className="text-xs bg-gray-100 rounded px-2 py-1">{c.trade}: {c.headcount} workers, {c.hours_worked}h</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {(!logs || logs.length === 0) && !showForm && (
        <div className="text-center py-12 text-gray-500">
          <BookOpen className="w-10 h-10 mx-auto mb-3 text-gray-300" />
          <p>No daily logs yet. Record your first day on site.</p>
        </div>
      )}
    </div>
  )
}
