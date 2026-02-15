import api from './client'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function sendMessage(
  projectId: number,
  message: string,
  history: ChatMessage[]
): Promise<string> {
  const res = await api.post(`/projects/${projectId}/chat`, { message, history })
  return res.data.response
}
