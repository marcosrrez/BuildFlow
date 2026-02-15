import { createContext, useContext, useState, ReactNode } from 'react'

interface EducationContextType {
  openTerm: (termId: string) => void;
  closeDrawer: () => void;
  activeTermId: string | null;
  isOpen: boolean;
}

const EducationContext = createContext<EducationContextType | undefined>(undefined)

export function EducationProvider({ children }: { children: ReactNode }) {
  const [activeTermId, setActiveTermId] = useState<string | null>(null)

  const openTerm = (termId: string) => {
    setActiveTermId(termId)
  }

  const closeDrawer = () => {
    setActiveTermId(null)
  }

  return (
    <EducationContext.Provider value={{ openTerm, closeDrawer, activeTermId, isOpen: !!activeTermId }}>
      {children}
    </EducationContext.Provider>
  )
}

export function useEducation() {
  const context = useContext(EducationContext)
  if (context === undefined) {
    throw new Error('useEducation must be used within an EducationProvider')
  }
  return context
}
