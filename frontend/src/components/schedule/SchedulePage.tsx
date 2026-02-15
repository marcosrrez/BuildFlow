import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { Activity, Milestone } from '../../types'
import StatusBadge from '../shared/StatusBadge'
import { Calendar, Plus, Zap, AlertTriangle, Trash2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function SchedulePage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [view, setView] = useState<'gantt' | 'list'>('gantt')

  const { data: activities } = useQuery<Activity[]>({
    queryKey: ['activities', projectId],
    queryFn: () => api.get(`/projects/${projectId}/schedule/activities`).then(r => r.data),
  })

  const { data: milestones } = useQuery<Milestone[]>({
    queryKey: ['milestones', projectId],
    queryFn: () => api.get(`/projects/${projectId}/schedule/milestones`).then(r => r.data),
  })

  const loadTemplate = useMutation({
    mutationFn: () => api.post(`/projects/${projectId}/schedule/template`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['activities'] }),
  })

  const deleteActivity = useMutation({
    mutationFn: (actId: number) => api.delete(`/projects/${projectId}/schedule/activities/${actId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['activities'] }),
  })

  const criticalPath = (activities || []).filter(a => a.is_critical)
  const maxFinish = Math.max(...(activities || []).map(a => a.early_finish), 1)

  const ganttData = (activities || []).map(a => ({
    name: a.name.length > 25 ? a.name.substring(0, 25) + '...' : a.name,
    start: a.early_start,
    duration: a.duration_days,
    isCritical: a.is_critical,
    float: a.total_float,
    status: a.status,
    code: a.activity_code,
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Schedule Manager</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setView(view === 'gantt' ? 'list' : 'gantt')}
            className="border px-3 py-2 rounded-lg text-sm hover:bg-gray-50"
          >
            {view === 'gantt' ? 'List View' : 'Gantt View'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Total Activities</p>
          <p className="text-2xl font-bold">{(activities || []).length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Critical Path</p>
          <p className="text-2xl font-bold text-red-600">{criticalPath.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Project Duration</p>
          <p className="text-2xl font-bold">{maxFinish} days</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-sm text-gray-500">Completed</p>
          <p className="text-2xl font-bold">{(activities || []).filter(a => a.status === 'completed').length}</p>
        </div>
      </div>

      {/* Load template */}
      {(!activities || activities.length === 0) && (
        <div className="bg-white rounded-xl shadow-sm border p-6 text-center">
          <Calendar className="w-10 h-10 text-blue-400 mx-auto mb-3" />
          <p className="text-gray-600 mb-3">Load a pre-built residential construction schedule template (28 activities with dependencies).</p>
          <button onClick={() => loadTemplate.mutate()} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Load Home Build Template
          </button>
        </div>
      )}

      {/* Gantt chart */}
      {view === 'gantt' && ganttData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" /> Schedule Timeline
            <span className="text-xs text-gray-400 ml-2">(Red = Critical Path)</span>
          </h2>
          <ResponsiveContainer width="100%" height={Math.max(400, ganttData.length * 28)}>
            <BarChart data={ganttData} layout="vertical" barSize={16}>
              <XAxis type="number" domain={[0, maxFinish]} label={{ value: 'Days', position: 'bottom' }} />
              <YAxis type="category" dataKey="name" width={200} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number, name: string) => [v + ' days', name === 'start' ? 'Start Day' : 'Duration']} />
              <Bar dataKey="start" stackId="a" fill="transparent" />
              <Bar dataKey="duration" stackId="a">
                {ganttData.map((entry, i) => (
                  <Cell key={i} fill={entry.isCritical ? '#ef4444' : '#3b82f6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* List view */}
      {view === 'list' && activities && activities.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium">Code</th>
                  <th className="text-left px-4 py-3 font-medium">Activity</th>
                  <th className="text-center px-4 py-3 font-medium">Days</th>
                  <th className="text-center px-4 py-3 font-medium">ES</th>
                  <th className="text-center px-4 py-3 font-medium">EF</th>
                  <th className="text-center px-4 py-3 font-medium">Float</th>
                  <th className="text-center px-4 py-3 font-medium">Critical</th>
                  <th className="text-center px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {activities.map(a => (
                  <tr key={a.id} className={`hover:bg-gray-50 ${a.is_critical ? 'bg-red-50' : ''}`}>
                    <td className="px-4 py-2.5 font-mono text-xs">{a.activity_code}</td>
                    <td className="px-4 py-2.5">{a.name}</td>
                    <td className="px-4 py-2.5 text-center">{a.duration_days}</td>
                    <td className="px-4 py-2.5 text-center text-gray-500">{a.early_start}</td>
                    <td className="px-4 py-2.5 text-center text-gray-500">{a.early_finish}</td>
                    <td className="px-4 py-2.5 text-center">{a.total_float}</td>
                    <td className="px-4 py-2.5 text-center">
                      {a.is_critical && <AlertTriangle className="w-4 h-4 text-red-500 inline" />}
                    </td>
                    <td className="px-4 py-2.5 text-center"><StatusBadge status={a.status} /></td>
                    <td className="px-4 py-2.5 text-center">
                      <button
                        onClick={() => { if (window.confirm(`Delete activity "${a.name}"?`)) deleteActivity.mutate(a.id) }}
                        className="text-gray-400 hover:text-red-500 p-1"
                        title="Delete activity"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
