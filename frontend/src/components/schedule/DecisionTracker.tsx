import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../../api/client'
import type { Decision, Activity } from '../../types'
import { format } from 'date-fns'
import { 
  CheckCircle2, Circle, Clock, AlertCircle, 
  BookOpen, ChevronRight, Save, X 
} from 'lucide-react'
import LearnTrigger from '../shared/LearnTrigger'

export default function DecisionTracker({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const [editingId, setEditingId] = useState<number | null>(null)
  const [choice, setChoice] = useState('')

  const { data: decisions, isLoading } = useQuery<Decision[]>({
    queryKey: ['decisions', projectId],
    queryFn: () => api.get(`/projects/${projectId}/schedule/decisions`).then(r => r.data),
  })

  const { data: activities } = useQuery<Activity[]>({
    queryKey: ['activities', projectId],
    queryFn: () => api.get(`/projects/${projectId}/schedule/activities`).then(r => r.data),
  })

  const makeDecision = useMutation({
    mutationFn: ({ id, choice }: { id: number, choice: string }) => 
      api.put(`/projects/${projectId}/schedule/decisions/${id}`, { 
        choice_made: choice, 
        status: 'decided' 
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['decisions'] })
      setEditingId(null)
      setChoice('')
    }
  })

  if (isLoading) return <div className="animate-pulse bg-gray-100 h-64 rounded-xl" />

  const pending = (decisions || []).filter(d => d.status === 'pending')
  const completed = (decisions || []).filter(d => d.status === 'decided')

  const ImpactBadge = ({ level }: { level: string }) => {
    const colors = {
      high: 'bg-red-100 text-red-700 border-red-200',
      medium: 'bg-amber-100 text-amber-700 border-amber-200',
      low: 'bg-blue-100 text-blue-700 border-blue-200',
    }
    return (
      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${colors[level as keyof typeof colors] || colors.medium}`}>
        {level} Impact
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Decision Tracker</h2>
          <p className="text-sm text-gray-500">Track critical selections and prevent schedule delays.</p>
        </div>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span>
            <span className="font-medium">{pending.length} Pending</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            <span className="font-medium">{completed.length} Decided</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Decisions */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">Upcoming Decisions</h3>
          {pending.length === 0 ? (
            <div className="bg-gray-50 rounded-xl border-2 border-dashed p-8 text-center">
              <CheckCircle2 className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">All caught up! No pending decisions.</p>
            </div>
          ) : (
            pending.map(d => {
              const activity = activities?.find(a => a.id === d.activity_id)
              const isEditing = editingId === d.id

              return (
                <div key={d.id} className="bg-white rounded-xl border shadow-sm hover:shadow-md transition-shadow p-4 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-gray-900">{d.title}</h4>
                        <ImpactBadge level={d.impact_level} />
                      </div>
                      <p className="text-sm text-gray-600 leading-relaxed">{d.description}</p>
                    </div>
                    {d.knowledge_term && (
                      <LearnTrigger term={d.knowledge_term} mode="icon" className="bg-blue-50 p-2 rounded-lg text-blue-500 hover:bg-blue-100" />
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-xs text-gray-500 pt-1">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      Due: {d.due_date ? format(new Date(d.due_date), 'MMM d, yyyy') : 'TBD'}
                    </div>
                    {activity && (
                      <div className="flex items-center gap-1 text-amber-600 font-medium">
                        <AlertCircle className="w-3.5 h-3.5" />
                        Affects: {activity.name}
                      </div>
                    )}
                  </div>

                  {isEditing ? (
                    <div className="pt-2 flex gap-2">
                      <input 
                        autoFocus
                        value={choice}
                        onChange={e => setChoice(e.target.value)}
                        placeholder="What did you decide? (e.g., 'Slab Foundation', 'Metal Roof')"
                        className="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                      <button 
                        onClick={() => makeDecision.mutate({ id: d.id, choice })}
                        disabled={!choice.trim() || makeDecision.isPending}
                        className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        <Save className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => setEditingId(null)}
                        className="p-2 text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <button 
                      onClick={() => setEditingId(d.id)}
                      className="w-full mt-2 flex items-center justify-between bg-gray-50 hover:bg-blue-50 hover:text-blue-700 text-gray-600 px-3 py-2 rounded-lg text-xs font-bold transition-colors group"
                    >
                      Log Your Decision
                      <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                  )}
                </div>
              )
            })
          )}
        </div>

        {/* Completed Decisions */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">Past Decisions</h3>
          <div className="bg-gray-50/50 rounded-xl border overflow-hidden">
            {completed.length === 0 ? (
              <div className="p-8 text-center text-gray-400 text-sm italic">
                No decisions logged yet.
              </div>
            ) : (
              <div className="divide-y">
                {completed.map(d => (
                  <div key={d.id} className="p-4 flex items-center justify-between gap-4 bg-white/50">
                    <div>
                      <h4 className="font-bold text-gray-700 text-sm">{d.title}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[11px] text-green-600 font-bold uppercase tracking-tight">Choice:</span>
                        <span className="text-xs text-gray-600">{d.choice_made}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-[10px] text-gray-400">
                        <CheckCircle2 className="w-3 h-3 text-green-500" />
                        {d.decided_at ? format(new Date(d.decided_at), 'MMM d') : 'Done'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
