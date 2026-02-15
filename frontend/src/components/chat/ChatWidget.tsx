import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Loader2 } from 'lucide-react'
import { sendMessage, type ChatMessage } from '../../api/chat'

const STARTERS = [
  "How's my budget looking?",
  "What's due this week?",
  "Am I on schedule?",
  "Any risks I should know about?",
]

export default function ChatWidget({ projectId }: { projectId: number }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text: string) => {
    if (!text.trim() || loading) return
    const userMsg: ChatMessage = { role: 'user', content: text.trim() }
    const history = [...messages, userMsg]
    setMessages(history)
    setInput('')
    setLoading(true)

    try {
      const response = await sendMessage(projectId, text.trim(), messages)
      setMessages([...history, { role: 'assistant', content: response }])
    } catch {
      setMessages([...history, { role: 'assistant', content: 'Sorry, I encountered an error. Please check that ANTHROPIC_API_KEY is set in your .env file.' }])
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-20 lg:bottom-6 right-4 z-50 bg-blue-600 text-white rounded-full p-3.5 shadow-lg hover:bg-blue-700 transition-all hover:scale-105"
        title="Ask BuildFlow AI"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    )
  }

  return (
    <div className="fixed bottom-20 lg:bottom-6 right-4 z-50 w-[360px] max-h-[500px] bg-white rounded-xl shadow-2xl border flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-blue-600 text-white rounded-t-xl">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          <span className="font-semibold text-sm">BuildFlow AI</span>
        </div>
        <button onClick={() => setIsOpen(false)}>
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-[200px] max-h-[340px]">
        {messages.length === 0 && (
          <div className="space-y-2">
            <p className="text-sm text-gray-500 text-center mb-3">
              Ask me anything about your project
            </p>
            {STARTERS.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="w-full text-left text-sm px-3 py-2 bg-gray-50 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors border"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] px-3 py-2 rounded-lg text-sm whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-sm'
                  : 'bg-gray-100 text-gray-800 rounded-bl-sm'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-3 py-2 flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t">
        <form
          onSubmit={(e) => { e.preventDefault(); send(input) }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your project..."
            className="flex-1 text-sm border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white rounded-lg px-3 py-2 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  )
}
