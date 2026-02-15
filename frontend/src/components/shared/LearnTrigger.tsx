import { HelpCircle } from 'lucide-react'
import { useEducation } from '../../contexts/EducationContext'

interface LearnTriggerProps {
  term: string;
  children?: React.ReactNode;
  mode?: 'icon' | 'text' | 'underline';
  className?: string;
}

export default function LearnTrigger({ term, children, mode = 'underline', className = '' }: LearnTriggerProps) {
  const { openTerm } = useEducation()

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    openTerm(term)
  }

  if (mode === 'icon') {
    return (
      <button 
        onClick={handleClick}
        className={`text-gray-400 hover:text-blue-500 transition-colors inline-flex items-center justify-center ${className}`}
        title={`Learn about ${term}`}
      >
        <HelpCircle className="w-4 h-4" />
      </button>
    )
  }

  if (mode === 'text') {
    return (
      <button 
        onClick={handleClick}
        className={`text-blue-600 hover:text-blue-800 hover:underline ${className}`}
      >
        {children || term}
      </button>
    )
  }

  // Default: subtle underline style for existing text
  return (
    <span 
      onClick={handleClick}
      className={`cursor-help decoration-dotted underline decoration-gray-400 underline-offset-2 hover:text-blue-600 hover:decoration-blue-400 transition-colors ${className}`}
    >
      {children || term}
    </span>
  )
}
