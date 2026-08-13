import * as React from "react"
import { api } from "../lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Bot, Send, Sparkles, User, Trash2, HelpCircle, Loader2 } from "lucide-react"

interface Message {
  sender: "user" | "assistant"
  text: string
  timestamp: Date
}

export function AIAssistantPanel() {
  const [messages, setMessages] = React.useState<Message[]>([])
  const [inputText, setInputText] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [suggestions, setSuggestions] = React.useState<string[]>([])
  const chatEndRef = React.useRef<HTMLDivElement>(null)

  // Load initial suggestions and welcome message
  React.useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const data = await api.getAISuggestions()
        setSuggestions(data)
      } catch (err) {
        // Fallback standard suggestions
        setSuggestions([
          "Колко устройства има в системата?",
          "Кои устройства са офлайн в момента?",
          "Има ли засичени сигурностни аномалии в конфигурациите?",
          "Как да конфигурирам OSPF маршрутизация на Cisco?"
        ])
      }
    }

    void fetchSuggestions()

    // Add welcoming message
    setMessages([
      {
        sender: "assistant",
        text: "Здравейте! Аз съм Вашият **AI Мрежов Асистент** (LANi Copilot) за платформата.\n\nМога да анализирам мрежовата среда, да докладвам статистики, офлайн устройства, да откривам сигурностни аномалии в реално време, или да Ви помогна с инструкции за CLI конфигурации и използването на самата платформа на български език.\n\nПопитайте ме нещо или изберете един от предложените въпроси по-долу!",
        timestamp: new Date()
      }
    ])
  }, [])

  // Auto scroll to latest message
  React.useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return

    const userMsg: Message = {
      sender: "user",
      text: textToSend,
      timestamp: new Date()
    }

    setMessages((prev) => [...prev, userMsg])
    setInputText("")
    setLoading(true)

    try {
      const response = await api.chatWithAI(textToSend)
      const assistantMsg: Message = {
        sender: "assistant",
        text: response.response,
        timestamp: new Date()
      }
      setMessages((prev) => [...prev, assistantMsg])
      if (response.suggested_queries && response.suggested_queries.length > 0) {
        setSuggestions(response.suggested_queries)
      }
    } catch (err) {
      const errorMsg: Message = {
        sender: "assistant",
        text: "❌ Съжалявам, възникна грешка при връзката с AI Асистента. Моля, опитайте отново.",
        timestamp: new Date()
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleClearChat = () => {
    setMessages([
      {
        sender: "assistant",
        text: "Разговорът беше нулиран. С какво мога да Ви помогна сега?",
        timestamp: new Date()
      }
    ])
  }

  // Basic Markdown and formatting renderer for rendering responses beautifully
  const renderMessageText = (text: string) => {
    const lines = text.split("\n")
    let inCodeBlock = false
    let codeBlockContent: string[] = []

    return lines.map((line, idx) => {
      // Toggle Code Blocks
      if (line.trim().startsWith("```")) {
        if (inCodeBlock) {
          inCodeBlock = false
          const content = codeBlockContent.join("\n")
          codeBlockContent = []
          return (
            <pre key={idx} className="my-2 overflow-x-auto rounded-md bg-zinc-950 p-3 text-xs text-zinc-100 font-mono border border-zinc-800">
              <code>{content}</code>
            </pre>
          )
        } else {
          inCodeBlock = true
          return null
        }
      }

      if (inCodeBlock) {
        codeBlockContent.push(line)
        return null
      }

      // Render Headings
      if (line.trim().startsWith("### ")) {
        return (
          <h4 key={idx} className="mt-3 mb-1 text-base font-bold text-foreground">
            {line.replace("### ", "")}
          </h4>
        )
      }
      if (line.trim().startsWith("#### ")) {
        return (
          <h5 key={idx} className="mt-2 mb-1 text-sm font-bold text-foreground opacity-90">
            {line.replace("#### ", "")}
          </h5>
        )
      }

      // Render Bullet Points
      if (line.trim().startsWith("• ") || line.trim().startsWith("- ")) {
        const cleanLine = line.trim().replace(/^[•-]\s+/, "")
        return (
          <li key={idx} className="ml-4 list-disc text-sm py-0.5 text-muted-foreground leading-relaxed">
            {parseBoldText(cleanLine)}
          </li>
        )
      }

      // Render standard paragraph with Bold replacement
      return (
        <p key={idx} className="text-sm py-1 leading-relaxed text-muted-foreground min-h-[1rem]">
          {parseBoldText(line)}
        </p>
      )
    })
  }

  // Parse **bold** in text
  const parseBoldText = (text: string) => {
    if (!text.includes("**")) return text

    const parts = text.split("**")
    return parts.map((part, index) => {
      // Odd indices are between **
      if (index % 2 === 1) {
        return <strong key={index} className="font-bold text-foreground">{part}</strong>
      }
      return part
    })
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-4 h-[calc(100vh-12rem)]">
      {/* Suggestions Sidebar */}
      <div className="lg:col-span-1 flex flex-col gap-4">
        <Card className="h-full flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary animate-pulse" />
              <span>Бързи Въпроси</span>
            </CardTitle>
            <CardDescription className="text-xs">
              Кликнете на някой от въпросите за незабавен AI анализ:
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-2 pb-4">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(s)}
                disabled={loading}
                className="w-full text-left p-2.5 rounded-lg border text-xs bg-accent/40 hover:bg-accent hover:border-primary/50 transition-all text-muted-foreground hover:text-accent-foreground flex items-start gap-2 disabled:opacity-50"
              >
                <HelpCircle className="h-3.5 w-3.5 mt-0.5 shrink-0 text-primary" />
                <span>{s}</span>
              </button>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Main Chat Interface */}
      <div className="lg:col-span-3 flex flex-col h-full">
        <Card className="flex flex-col h-full overflow-hidden">
          {/* Header */}
          <CardHeader className="border-b py-3 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <CardTitle className="text-base">AI Мрежов Асистент (Copilot)</CardTitle>
                <CardDescription className="text-xs">Реални мрежови анализи, одит и инструкции на български</CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearChat}
              title="Изчисти чата"
              className="text-muted-foreground hover:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              <span className="text-xs hidden md:inline">Изчисти</span>
            </Button>
          </CardHeader>

          {/* Messages Body */}
          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/10">
            {messages.map((msg, index) => {
              const isAssistant = msg.sender === "assistant"
              return (
                <div
                  key={index}
                  className={`flex gap-3 max-w-[85%] ${
                    isAssistant ? "mr-auto" : "ml-auto flex-row-reverse"
                  }`}
                >
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 border ${
                      isAssistant
                        ? "bg-primary/10 text-primary border-primary/20"
                        : "bg-secondary text-secondary-foreground"
                    }`}
                  >
                    {isAssistant ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                  </div>
                  <div
                    className={`rounded-lg px-3.5 py-2.5 shadow-sm border ${
                      isAssistant
                        ? "bg-card text-card-foreground border-border"
                        : "bg-primary text-primary-foreground border-primary"
                    }`}
                  >
                    <div className="space-y-1">
                      {isAssistant ? (
                        renderMessageText(msg.text)
                      ) : (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                      )}
                      <span
                        className={`text-[10px] block text-right mt-1.5 ${
                          isAssistant ? "text-muted-foreground" : "text-primary-foreground/70"
                        }`}
                      >
                        {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
            {loading && (
              <div className="flex gap-3 mr-auto max-w-[85%]">
                <div className="h-8 w-8 rounded-full flex items-center justify-center shrink-0 bg-primary/10 text-primary border border-primary/20">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="rounded-lg px-4 py-3 bg-card border border-border shadow-sm flex items-center gap-2">
                  <Loader2 className="h-4 w-4 text-primary animate-spin" />
                  <span className="text-xs text-muted-foreground font-medium">Асистентът анализира мрежата в реално време...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </CardContent>

          {/* Footer Input */}
          <CardFooter className="border-t p-3 bg-card">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (inputText.trim()) {
                  void handleSendMessage(inputText)
                }
              }}
              className="flex w-full items-center gap-2"
            >
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Задайте въпрос (напр. 'кои устройства са офлайн?', 'анализирай сигурността')..."
                disabled={loading}
                className="flex-1 bg-muted/30 focus-visible:ring-1 focus-visible:ring-primary text-sm"
              />
              <Button type="submit" size="icon" disabled={!inputText.trim() || loading} className="shrink-0">
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
