import { useState, type FormEvent, useEffect, useRef } from 'react'
import './App.css'

// define Message type
interface Message {
  id: string
  text: string
  sender: 'user' | 'assistant'
}

const API_BASE = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const makeId = () =>
    (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`)

  // when messages change, scroll to the bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // adaptive height of input text-area
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 240) + 'px'
  }, [inputValue])

  // handle form submit event
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const rawInput = inputValue.trim()
    if (!rawInput.trim()) return

    // create user message
    const userId = makeId()
    const userMessage: Message = { id: userId, text: rawInput, sender: 'user' }
    setMessages(prev => [...prev, userMessage])
    setInputValue('') // clear input

    // insert a blank assistant message
    const assistantId = makeId()
    setMessages(prev => [...prev, { id: assistantId, text: '', sender: 'assistant' }])

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Accept': 'text/event-stream'},
        body: JSON.stringify({ message: rawInput }),
      })
      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        
        // SSE split events
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // the last one may be incomplete

        for (const evt of events) {
          const line = evt.split('\n').find(l => l.startsWith('data:'))
          if (!line) continue
          const raw = line.slice(5).trimStart() // remove 'data: ' prefix
          try {
            const obj = JSON.parse(raw)
            if (obj.end) {
              reader.cancel()
              break
            }
            if (typeof obj.token === 'string') {
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === assistantId ? { ...msg, text: msg.text + obj.token } : msg
                )
              )
            }
          } catch (e) {
            console.error('error parsing SSE data:', e)
          }
        }
      }
    } catch (err: any) {
      console.error('Error:', err)
      setMessages(prev => 
        prev.map(msg => 
          msg.id === assistantId 
          ? {...msg, text: 'Error occurred' + (err.message || String(err))} 
          : msg
        )
      )
    }
  }

  // handle Enter / Shift + Enter / Tab
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      // trigger form submit
      e.preventDefault()
      ;(e.currentTarget.form as HTMLFormElement)?.requestSubmit()
      return
    }
    if (e.key === 'Tab') {
      e.preventDefault()
      const el = e.currentTarget
      const start = el.selectionStart
      const end = el.selectionEnd
      const newValue = inputValue.slice(0, start) + '\t' + inputValue.slice(end)
      setInputValue(newValue)
      requestAnimationFrame(() => {
        el.selectionStart = el.selectionEnd = start + 1
      })
    }
  }

  return (
    <div className='chat-container'>
      <div className='messages-list'>
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}-message`}>
            {msg.sender === 'assistant'
              ? <div className='assistant-text'>{msg.text}</div>
              : <div className='user-text'>{msg.text}</div>
            }
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className='chat-input-form' onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Type your message...'
          rows={1}
          // style={{ resize: 'none' }}
        />
        <button type='submit'>↑</button>
      </form>
    </div>
  )
}

export default App