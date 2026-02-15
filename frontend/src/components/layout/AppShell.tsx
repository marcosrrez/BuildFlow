import { ReactNode, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/client'
import type { Project } from '../../types'
import {
  LayoutDashboard, DollarSign, Calendar, FileCheck,
  ClipboardCheck, BookOpen, FolderOpen, Users, Menu, X, Hammer,
  ChevronDown, Plus,
} from 'lucide-react'
import NotificationBell from '../shared/NotificationBell'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/budget', icon: DollarSign, label: 'Budget' },
  { to: '/schedule', icon: Calendar, label: 'Schedule' },
  { to: '/permits', icon: FileCheck, label: 'Permits' },
  { to: '/punchlist', icon: ClipboardCheck, label: 'Punch List' },
  { to: '/daily-log', icon: BookOpen, label: 'Daily Log' },
  { to: '/documents', icon: FolderOpen, label: 'Documents' },
  { to: '/subcontractors', icon: Users, label: 'Subs' },
]

interface AppShellProps {
  children: ReactNode
  projectId: number
  onProjectChange?: (id: number) => void
}

export default function AppShell({ children, projectId, onProjectChange }: AppShellProps) {
  const [open, setOpen] = useState(false)
  const [showProjectMenu, setShowProjectMenu] = useState(false)
  const [showNewProject, setShowNewProject] = useState(false)
  const qc = useQueryClient()

  const { data: projects } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: () => api.get('/projects').then(r => r.data),
  })

  const createProject = useMutation({
    mutationFn: (data: any) => api.post('/projects', data),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      onProjectChange?.(res.data.id)
      setShowNewProject(false)
      setShowProjectMenu(false)
    },
  })

  const currentProject = (projects || []).find(p => p.id === projectId)
  const projectName = currentProject?.name || 'Select Project'

  const ProjectSelector = ({ mobile }: { mobile?: boolean }) => (
    <div className="relative px-2 mb-3">
      <button
        onClick={() => setShowProjectMenu(!showProjectMenu)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-sm text-left"
      >
        <span className="truncate text-gray-100">{projectName}</span>
        <ChevronDown className={`w-4 h-4 text-gray-400 shrink-0 transition-transform ${showProjectMenu ? 'rotate-180' : ''}`} />
      </button>

      {showProjectMenu && (
        <div className="absolute left-2 right-2 top-full mt-1 bg-gray-800 rounded-lg border border-gray-700 shadow-lg z-50 max-h-64 overflow-y-auto">
          {(projects || []).map(p => (
            <button
              key={p.id}
              onClick={() => {
                onProjectChange?.(p.id)
                setShowProjectMenu(false)
                if (mobile) setOpen(false)
              }}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-700 first:rounded-t-lg ${
                p.id === projectId ? 'text-blue-400 bg-gray-700' : 'text-gray-300'
              }`}
            >
              <span className="block truncate">{p.name}</span>
              {p.address && <span className="block text-xs text-gray-500 truncate">{p.address}</span>}
            </button>
          ))}
          <button
            onClick={() => { setShowNewProject(true); setShowProjectMenu(false) }}
            className="w-full text-left px-3 py-2 text-sm text-green-400 hover:bg-gray-700 border-t border-gray-700 last:rounded-b-lg flex items-center gap-2"
          >
            <Plus className="w-4 h-4" /> New Project
          </button>
        </div>
      )}
    </div>
  )

  const NewProjectModal = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={() => setShowNewProject(false)} />
      <form
        className="relative bg-white rounded-xl shadow-xl p-6 w-full max-w-md space-y-4 z-50"
        onSubmit={e => {
          e.preventDefault()
          const fd = new FormData(e.currentTarget)
          createProject.mutate({
            name: fd.get('name'),
            address: fd.get('address') || undefined,
            city: fd.get('city') || undefined,
            state: fd.get('state') || undefined,
            total_budget: Number(fd.get('total_budget') || 0),
          })
        }}
      >
        <h2 className="text-lg font-bold text-gray-900">Create New Project</h2>
        <div className="space-y-3">
          <input name="name" placeholder="Project name (e.g., My Dream Home)" required className="w-full border rounded-lg px-3 py-2 text-sm" />
          <input name="address" placeholder="Address" className="w-full border rounded-lg px-3 py-2 text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <input name="city" placeholder="City" className="border rounded-lg px-3 py-2 text-sm" />
            <input name="state" placeholder="State" className="border rounded-lg px-3 py-2 text-sm" />
          </div>
          <input name="total_budget" type="number" step="0.01" placeholder="Total budget ($)" className="w-full border rounded-lg px-3 py-2 text-sm" />
        </div>
        <div className="flex gap-2 pt-2">
          <button type="submit" disabled={createProject.isPending} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            {createProject.isPending ? 'Creating...' : 'Create Project'}
          </button>
          <button type="button" onClick={() => setShowNewProject(false)} className="text-gray-500 px-4 py-2 text-sm">Cancel</button>
        </div>
      </form>
    </div>
  )

  return (
    <div className="min-h-screen flex">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-56 bg-gray-900 text-white fixed inset-y-0 z-30">
        <div className="flex items-center gap-2 px-4 py-4 border-b border-gray-700">
          <Hammer className="w-6 h-6 text-blue-400" />
          <span className="font-bold text-lg">BuildFlow</span>
        </div>
        <div className="pt-3">
          <ProjectSelector />
        </div>
        <nav className="flex-1 py-2 space-y-1 px-2">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Mobile overlay */}
      {open && (
        <div className="lg:hidden fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="relative w-64 bg-gray-900 text-white flex flex-col z-50">
            <div className="flex items-center justify-between px-4 py-4 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <Hammer className="w-6 h-6 text-blue-400" />
                <span className="font-bold text-lg">BuildFlow</span>
              </div>
              <button onClick={() => setOpen(false)}><X className="w-5 h-5" /></button>
            </div>
            <div className="pt-3">
              <ProjectSelector mobile />
            </div>
            <nav className="flex-1 py-2 space-y-1 px-2">
              {NAV.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                      isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 lg:ml-56 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="flex items-center gap-3 px-4 py-3 bg-white border-b sticky top-0 z-20">
          <button onClick={() => setOpen(true)} className="lg:hidden">
            <Menu className="w-6 h-6 text-gray-600" />
          </button>
          <Hammer className="w-5 h-5 text-blue-600 lg:hidden" />
          <span className="font-bold text-gray-800 lg:hidden">BuildFlow</span>
          <div className="ml-auto">
            <NotificationBell projectId={projectId} />
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          {children}
        </main>

        {/* Mobile bottom nav - 4 key tabs */}
        <nav className="lg:hidden fixed bottom-0 inset-x-0 bg-white border-t flex z-20">
          {NAV.slice(0, 4).map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex-1 flex flex-col items-center py-2 text-xs ${
                  isActive ? 'text-blue-600' : 'text-gray-500'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="mt-0.5">{label}</span>
            </NavLink>
          ))}
          <button
            onClick={() => setOpen(true)}
            className="flex-1 flex flex-col items-center py-2 text-xs text-gray-500"
          >
            <Menu className="w-5 h-5" />
            <span className="mt-0.5">More</span>
          </button>
        </nav>
      </div>

      {showNewProject && <NewProjectModal />}
    </div>
  )
}
