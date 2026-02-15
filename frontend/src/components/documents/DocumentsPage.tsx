import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRef } from 'react'
import api from '../../api/client'
import type { DocRecord } from '../../types'
import { FolderOpen, Upload, FileText, Download, Trash2 } from 'lucide-react'

function formatBytes(bytes: number | undefined): string {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

export default function DocumentsPage({ projectId }: { projectId: number }) {
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)

  const { data: docs } = useQuery<DocRecord[]>({
    queryKey: ['documents', projectId],
    queryFn: () => api.get(`/projects/${projectId}/documents`).then(r => r.data),
  })

  const uploadDoc = useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('name', file.name)
      return api.post(`/projects/${projectId}/documents`, fd)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents'] }),
  })

  const deleteDoc = useMutation({
    mutationFn: (id: number) => api.delete(`/projects/${projectId}/documents/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents'] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <button onClick={() => fileRef.current?.click()} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Upload className="w-4 h-4" /> Upload
        </button>
        <input ref={fileRef} type="file" className="hidden" onChange={e => {
          const f = e.target.files?.[0]
          if (f) uploadDoc.mutate(f)
          e.target.value = ''
        }} />
      </div>

      {/* Drop zone */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
        onClick={() => fileRef.current?.click()}
        onDragOver={e => { e.preventDefault(); e.currentTarget.classList.add('border-blue-400') }}
        onDragLeave={e => { e.currentTarget.classList.remove('border-blue-400') }}
        onDrop={e => {
          e.preventDefault()
          e.currentTarget.classList.remove('border-blue-400')
          const f = e.dataTransfer.files?.[0]
          if (f) uploadDoc.mutate(f)
        }}
      >
        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-500">Drag and drop files here, or click to browse</p>
      </div>

      {/* Document list */}
      {docs && docs.length > 0 ? (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium">Name</th>
                <th className="text-left px-4 py-3 font-medium">Type</th>
                <th className="text-right px-4 py-3 font-medium">Size</th>
                <th className="text-left px-4 py-3 font-medium">Uploaded</th>
                <th className="text-right px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {docs.map(doc => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-gray-400" />
                    {doc.name}
                  </td>
                  <td className="px-4 py-3 text-gray-500 uppercase text-xs">{doc.file_type || '-'}</td>
                  <td className="px-4 py-3 text-right text-gray-500">{formatBytes(doc.file_size)}</td>
                  <td className="px-4 py-3 text-gray-500">{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      <a href={`/api/v1/projects/${projectId}/documents/${doc.id}/download`} className="text-blue-600 hover:text-blue-800">
                        <Download className="w-4 h-4" />
                      </a>
                      <button onClick={() => deleteDoc.mutate(doc.id)} className="text-red-400 hover:text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <FolderOpen className="w-10 h-10 mx-auto mb-3 text-gray-300" />
          <p>No documents yet. Upload contracts, permits, plans, and more.</p>
        </div>
      )}
    </div>
  )
}
