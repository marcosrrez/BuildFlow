import { useQuery } from '@tanstack/react-query'
import { X, BookOpen, AlertTriangle, ThumbsUp, ThumbsDown, Link as LinkIcon } from 'lucide-react'
import { useEducation } from '../../contexts/EducationContext'
import api from '../../api/client'
import type { KnowledgeEntry } from '../../types'

export default function EducationDrawer() {
  const { activeTermId, closeDrawer, isOpen, openTerm } = useEducation()

  const { data: entry, isLoading } = useQuery<KnowledgeEntry>({
    queryKey: ['education', activeTermId],
    queryFn: () => api.get(`/education/term/${activeTermId}`).then(r => r.data),
    enabled: !!activeTermId,
  })

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[60] flex justify-end">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/20 backdrop-blur-[2px] transition-opacity" 
        onClick={closeDrawer}
      />

      {/* Drawer */}
      <div className="relative w-full max-w-md bg-white shadow-2xl h-full overflow-y-auto flex flex-col border-l animate-in slide-in-from-right duration-300">
        
        {/* Header */}
        <div className="sticky top-0 bg-white/95 backdrop-blur z-10 border-b px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-700">
            <BookOpen className="w-5 h-5" />
            <span className="font-bold text-sm uppercase tracking-wide">Builder's Knowledge Base</span>
          </div>
          <button onClick={closeDrawer} className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-8">
          {isLoading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-full" />
              <div className="h-4 bg-gray-200 rounded w-5/6" />
              <div className="h-32 bg-gray-100 rounded-xl" />
            </div>
          ) : entry ? (
            <>
              {/* Title & Definition */}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{entry.title}</h2>
                <p className="text-lg text-gray-600 leading-relaxed font-medium">{entry.short_description}</p>
              </div>

              <div className="prose prose-blue prose-sm text-gray-600">
                <p>{entry.full_description}</p>
              </div>

              {/* Pros & Cons Grid */}
              <div className="grid grid-cols-1 gap-4">
                <div className="bg-green-50 rounded-xl p-4 border border-green-100">
                  <div className="flex items-center gap-2 mb-3 text-green-800 font-semibold">
                    <ThumbsUp className="w-4 h-4" />
                    <h3>Benefits</h3>
                  </div>
                  <ul className="space-y-2">
                    {entry.pros.map((p, i) => (
                      <li key={i} className="text-sm text-green-900 flex items-start gap-2">
                        <span className="block w-1.5 h-1.5 rounded-full bg-green-400 mt-1.5 shrink-0" />
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-orange-50 rounded-xl p-4 border border-orange-100">
                  <div className="flex items-center gap-2 mb-3 text-orange-800 font-semibold">
                    <ThumbsDown className="w-4 h-4" />
                    <h3>Drawbacks</h3>
                  </div>
                  <ul className="space-y-2">
                    {entry.cons.map((c, i) => (
                      <li key={i} className="text-sm text-orange-900 flex items-start gap-2">
                        <span className="block w-1.5 h-1.5 rounded-full bg-orange-400 mt-1.5 shrink-0" />
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Risks - What to watch out for */}
              <div className="bg-red-50 rounded-xl p-5 border border-red-100">
                <div className="flex items-center gap-2 mb-3 text-red-800 font-bold uppercase text-xs tracking-wider">
                  <AlertTriangle className="w-4 h-4" />
                  What to Watch Out For
                </div>
                <ul className="space-y-3">
                  {entry.risks.map((risk, i) => (
                    <li key={i} className="text-sm text-red-900 flex gap-3">
                      <span className="font-bold text-red-300">!</span>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Related Terms */}
              {entry.related_terms.length > 0 && (
                <div className="pt-4 border-t">
                  <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-3">Related Topics</span>
                  <div className="flex flex-wrap gap-2">
                    {entry.related_terms.map(term => (
                      <button 
                        key={term}
                        onClick={() => openTerm(term)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-600 text-xs font-medium hover:bg-blue-50 hover:text-blue-600 transition-colors"
                      >
                        <LinkIcon className="w-3 h-3" />
                        {term}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <BookOpen className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>Content not found for this topic.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
