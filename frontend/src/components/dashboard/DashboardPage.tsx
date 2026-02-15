import { useQuery } from '@tanstack/react-query'
import api from '../../api/client'
import type { DashboardSummary } from '../../types'
import StatCard from '../shared/StatCard'
import StatusBadge from '../shared/StatusBadge'
import LearnTrigger from '../shared/LearnTrigger'
import { formatCurrency, formatPercent } from '../../utils/constants'
import { DollarSign, Calendar, AlertTriangle, Clock, CloudSun, TrendingUp, Target } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface KPIMetric {
  name: string; category: string; current_value: number; target_value: number;
  unit: string; status: string; description?: string;
}

interface KPIResult {
  project_name: string; schedule_kpis: KPIMetric[]; cost_kpis: KPIMetric[]; quality_kpis: KPIMetric[];
}

interface CashFlowPeriod {
  period_label: string; planned_spend: number; actual_spend: number;
  cumulative_planned: number; cumulative_actual: number;
}

interface CashFlowResult {
  project_name: string; total_budget: number; total_spent: number; periods: CashFlowPeriod[];
}

function KPICard({ metric }: { metric: KPIMetric }) {
  const statusColors: Record<string, string> = {
    on_track: 'text-green-600 bg-green-50 border-green-200',
    at_risk: 'text-amber-600 bg-amber-50 border-amber-200',
    critical: 'text-red-600 bg-red-50 border-red-200',
  }
  const style = statusColors[metric.status] || 'text-gray-600 bg-gray-50 border-gray-200'

  return (
    <div className={`rounded-lg border p-3 ${style}`}>
      <div className="text-xs font-medium opacity-75 mb-1 flex items-center justify-between">
        {metric.name}
        <LearnTrigger term={metric.name} mode="icon" className="text-current opacity-50 hover:opacity-100" />
      </div>
      <div className="text-2xl font-bold">
        {metric.current_value}{metric.unit === '%' ? '%' : ''}
        {metric.unit === 'ratio' && <span className="text-sm font-normal ml-1">/ {metric.target_value}</span>}
      </div>
      {metric.description && <div className="text-xs mt-1 opacity-60">{metric.description}</div>}
    </div>
  )
}

export default function DashboardPage({ projectId }: { projectId: number }) {
  const { data, isLoading, error } = useQuery<DashboardSummary>({
    queryKey: ['dashboard', projectId],
    queryFn: () => api.get(`/projects/${projectId}/dashboard/summary`).then(r => r.data),
  })

  const { data: kpis } = useQuery<KPIResult>({
    queryKey: ['kpis', projectId],
    queryFn: () => api.get(`/projects/${projectId}/dashboard/kpis`).then(r => r.data),
    enabled: !!data,
  })

  const { data: cashflow } = useQuery<CashFlowResult>({
    queryKey: ['cashflow', projectId],
    queryFn: () => api.get(`/projects/${projectId}/budget/cashflow-forecast`).then(r => r.data),
    enabled: !!data,
  })

  if (isLoading) return <div className="animate-pulse text-gray-400 py-12 text-center">Loading dashboard...</div>
  if (error || !data) return (
    <div className="text-center py-12">
      <h2 className="text-xl font-bold text-gray-800 mb-2">Welcome to BuildFlow</h2>
      <p className="text-gray-500 mb-4">Create your first project to get started.</p>
      <button
        onClick={() => {
          api.post('/projects', { name: 'My Home Build', total_budget: 350000 }).then(() => window.location.reload())
        }}
        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
      >
        Create Project
      </button>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{data.project_name}</h1>
          <StatusBadge status={data.project_status} />
        </div>
        {data.weather && (
          <div className="flex items-center gap-2 text-sm text-gray-600 bg-white rounded-lg px-4 py-2 shadow-sm">
            <CloudSun className="w-5 h-5 text-yellow-500" />
            <span>{data.weather.temp ? `${Math.round(data.weather.temp)}F` : '--'}</span>
            <span className="text-gray-400">|</span>
            <span>{data.weather.condition || 'N/A'}</span>
          </div>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Budget"
          value={formatCurrency(data.budget.total_budget)}
          subtitle={`Spent: ${formatCurrency(data.budget.total_spent)}`}
          icon={<DollarSign className="w-5 h-5" />}
          status={data.budget.status as any}
        />
        <StatCard
          title="Budget Variance"
          value={formatCurrency(data.budget.variance)}
          subtitle={`${formatPercent(data.budget.variance_percent)}`}
          icon={<DollarSign className="w-5 h-5" />}
          status={data.budget.status as any}
        />
        <StatCard
          title="Schedule Progress"
          value={formatPercent(data.schedule.percent_complete)}
          subtitle={`${data.schedule.completed_activities}/${data.schedule.total_activities} activities`}
          icon={<Calendar className="w-5 h-5" />}
          status={data.schedule.status as any}
        />
        <StatCard
          title="Days Remaining"
          value={data.schedule.days_remaining}
          subtitle={`${data.schedule.critical_count} critical activities`}
          icon={<Clock className="w-5 h-5" />}
          status={data.schedule.status as any}
        />
      </div>

      {/* KPI Section */}
      {kpis && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-blue-500" /> Project KPIs
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {kpis.cost_kpis.map((m) => <KPICard key={m.name} metric={m} />)}
            {kpis.schedule_kpis.map((m) => <KPICard key={m.name} metric={m} />)}
          </div>
        </div>
      )}

      {/* Cash Flow S-Curve */}
      {cashflow && cashflow.periods.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-500" /> Cash Flow (Cumulative)
          </h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={cashflow.periods}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period_label" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={60} />
              <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
              <Legend />
              <Line type="monotone" dataKey="cumulative_planned" name="Planned" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="cumulative_actual" name="Actual" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alerts */}
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" /> Alerts
          </h2>
          {data.alerts.length === 0 ? (
            <p className="text-sm text-gray-500">No active alerts</p>
          ) : (
            <div className="space-y-2">
              {data.alerts.map((a, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <StatusBadge status={a.severity} />
                  <span className="text-gray-700">{a.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Upcoming Deadlines */}
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-500" /> Upcoming Deadlines
          </h2>
          {data.deadlines.length === 0 ? (
            <p className="text-sm text-gray-500">No upcoming deadlines</p>
          ) : (
            <div className="space-y-2">
              {data.deadlines.map((d, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{d.description}</span>
                  <span className={`font-medium ${d.days_until <= 3 ? 'text-red-600' : 'text-gray-500'}`}>
                    {d.days_until === 0 ? 'Today' : `${d.days_until}d`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quality KPIs */}
      {kpis && kpis.quality_kpis.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Quality Metrics</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {kpis.quality_kpis.map((m) => <KPICard key={m.name} metric={m} />)}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {data.recent_activity.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Recent Activity</h2>
          <div className="space-y-2">
            {data.recent_activity.map((a, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <StatusBadge status={a.module} />
                <span className="text-gray-700">{a.description}</span>
                <span className="text-gray-400 ml-auto text-xs">{new Date(a.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
