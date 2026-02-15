import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import AppShell from './components/layout/AppShell'
import DashboardPage from './components/dashboard/DashboardPage'
import BudgetPage from './components/budget/BudgetPage'
import SchedulePage from './components/schedule/SchedulePage'
import PermitsPage from './components/permits/PermitsPage'
import PunchListPage from './components/punchlist/PunchListPage'
import DailyLogPage from './components/daily-log/DailyLogPage'
import DocumentsPage from './components/documents/DocumentsPage'
import SubcontractorsPage from './components/subcontractors/SubcontractorsPage'
import ChatWidget from './components/chat/ChatWidget'
import { EducationProvider } from './contexts/EducationContext'
import EducationDrawer from './components/shared/EducationDrawer'

export default function App() {
  const qc = useQueryClient()
  const [projectId, setProjectId] = useState(() => {
    const saved = localStorage.getItem('buildflow_project_id')
    return saved ? Number(saved) : 1
  })

  const handleProjectChange = (id: number) => {
    setProjectId(id)
    // Clear all cached queries so every page fetches fresh data for the new project
    qc.removeQueries()
  }

  useEffect(() => {
    localStorage.setItem('buildflow_project_id', String(projectId))
  }, [projectId])

  return (
    <EducationProvider>
      <AppShell projectId={projectId} onProjectChange={handleProjectChange}>
        <Routes>
          <Route path="/" element={<DashboardPage projectId={projectId} />} />
          <Route path="/budget" element={<BudgetPage projectId={projectId} />} />
          <Route path="/schedule" element={<SchedulePage projectId={projectId} />} />
          <Route path="/permits" element={<PermitsPage projectId={projectId} />} />
          <Route path="/punchlist" element={<PunchListPage projectId={projectId} />} />
          <Route path="/daily-log" element={<DailyLogPage projectId={projectId} />} />
          <Route path="/documents" element={<DocumentsPage projectId={projectId} />} />
          <Route path="/subcontractors" element={<SubcontractorsPage projectId={projectId} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ChatWidget projectId={projectId} />
        <EducationDrawer />
      </AppShell>
    </EducationProvider>
  )
}
