const colors: Record<string, string> = {
  on_track: 'bg-green-100 text-green-800',
  at_risk: 'bg-yellow-100 text-yellow-800',
  critical: 'bg-red-100 text-red-800',
  Open: 'bg-blue-100 text-blue-800',
  Assigned: 'bg-purple-100 text-purple-800',
  'In Progress': 'bg-yellow-100 text-yellow-800',
  Completed: 'bg-green-100 text-green-800',
  Verified: 'bg-green-200 text-green-900',
  Rejected: 'bg-red-100 text-red-800',
  draft: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  under_review: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  issued: 'bg-green-200 text-green-900',
  active: 'bg-green-100 text-green-800',
  completed: 'bg-green-200 text-green-900',
  not_started: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-blue-100 text-blue-800',
  delayed: 'bg-red-100 text-red-800',
  invoiced: 'bg-yellow-100 text-yellow-800',
  paid: 'bg-green-100 text-green-800',
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  conditional: 'bg-yellow-100 text-yellow-800',
}

export default function StatusBadge({ status }: { status: string }) {
  const cls = colors[status] || 'bg-gray-100 text-gray-800'
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {status}
    </span>
  )
}
