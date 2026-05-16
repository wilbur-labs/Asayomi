import { useState } from 'react'
import { Input, Button, Typography, Spin, Tag, Space, Card, Empty } from 'antd'
import { MessageOutlined, SendOutlined, LinkOutlined } from '@ant-design/icons'
import { askChat } from '../services/api'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: { id: number; title: string; url: string; category: string }[]
}

const SUGGESTIONS = [
  '今日のテック界で何が起きた？',
  '最近の経済ニュースをまとめて',
  '国際情勢で注目すべきトピックは？',
  '日本の重要なニュース 3 つ教えて',
]

export default function ChatPage() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const send = async (q: string) => {
    if (!q.trim() || loading) return
    setMessages((m) => [...m, { role: 'user', content: q }])
    setInput('')
    setLoading(true)
    try {
      const res = await askChat(q)
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: res.data.answer, sources: res.data.sources },
      ])
    } catch (e: any) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `エラー: ${e.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <MessageOutlined style={{ marginRight: 8, color: '#8b5cf6' }} />
          AI チャット
        </Title>
        <Text type="secondary">直近のニュースを文脈にした AI アシスタント</Text>
      </div>

      <div
        style={{
          background: 'var(--card-bg, #fff)',
          padding: 20,
          borderRadius: 12,
          minHeight: 400,
          marginBottom: 16,
          boxShadow: 'var(--shadow-card)',
        }}
      >
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Empty description="質問してみましょう" />
            <Space wrap style={{ marginTop: 16, justifyContent: 'center' }}>
              {SUGGESTIONS.map((s) => (
                <Tag
                  key={s}
                  style={{ cursor: 'pointer', padding: '6px 12px', fontSize: 13 }}
                  color="blue"
                  onClick={() => send(s)}
                >
                  {s}
                </Tag>
              ))}
            </Space>
          </div>
        ) : (
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Card
                  size="small"
                  style={{
                    maxWidth: '80%',
                    background:
                      m.role === 'user'
                        ? 'var(--gradient-primary)'
                        : 'var(--tag-bg, #f3f4f6)',
                    color: m.role === 'user' ? '#fff' : undefined,
                    border: 'none',
                  }}
                  styles={{ body: { color: m.role === 'user' ? '#fff' : undefined } }}
                >
                  <Paragraph
                    style={{
                      whiteSpace: 'pre-wrap',
                      margin: 0,
                      color: m.role === 'user' ? '#fff' : undefined,
                    }}
                  >
                    {m.content}
                  </Paragraph>
                  {m.sources && m.sources.length > 0 && (
                    <div style={{ marginTop: 12, paddingTop: 8, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                      <Text strong style={{ fontSize: 12 }}>参考記事</Text>
                      <ol style={{ margin: '6px 0 0', paddingLeft: 20, fontSize: 12 }}>
                        {m.sources.slice(0, 5).map((s, idx) => (
                          <li key={s.id}>
                            <a href={s.url} target="_blank" rel="noopener">
                              [{idx + 1}] {s.title}
                              <LinkOutlined style={{ marginLeft: 4 }} />
                            </a>
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}
                </Card>
              </div>
            ))}
            {loading && <Spin />}
          </Space>
        )}
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <TextArea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="質問を入力（Cmd/Ctrl + Enter で送信）"
          autoSize={{ minRows: 1, maxRows: 4 }}
          onPressEnter={(e) => {
            if (e.metaKey || e.ctrlKey) {
              e.preventDefault()
              send(input)
            }
          }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={() => send(input)}
          loading={loading}
          disabled={!input.trim()}
        >
          送信
        </Button>
      </div>
    </div>
  )
}
