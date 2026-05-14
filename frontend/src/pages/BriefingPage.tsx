import { useEffect, useState } from 'react'
import { DatePicker, Empty, Spin, Typography, Row, Col, Button, message } from 'antd'
import { FileTextOutlined, ThunderboltOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import axios from 'axios'
import { getBriefings } from '../services/api'

const { Title, Text } = Typography

const CATEGORY_GRADIENT: Record<string, string> = {
  総合: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  テクノロジー: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  '経済・ビジネス': 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
  国際: 'linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)',
}

function renderBriefingBody(content: string) {
  // markdown 風のテキストを軽く HTML に
  const html = content
    .replace(/^## .+$/gm, '') // タイトル削除（カテゴリヘッダで表示してるため）
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(
      /(https?:\/\/[^\s)]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>'
    )
  return { __html: html }
}

export default function BriefingPage() {
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [briefings, setBriefings] = useState<{ category: string; content: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

  const fetchBriefings = () => {
    setLoading(true)
    getBriefings(date)
      .then((res) => setBriefings(res.data.briefings))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchBriefings()
  }, [date])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res = await axios.post('/api/v1/system/briefing')
      message.success(res.data.message)
      fetchBriefings()
    } catch {
      message.error('生成に失敗しました')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <FileTextOutlined style={{ marginRight: 8, color: '#4f46e5' }} />
          今日のブリーフィング
        </Title>
        <Text type="secondary">カテゴリ別のトップニュース要約</Text>
      </div>

      <div
        style={{
          background: '#fff',
          padding: 16,
          borderRadius: 12,
          marginBottom: 16,
          boxShadow: 'var(--shadow-card)',
          display: 'flex',
          gap: 12,
          alignItems: 'center',
        }}
      >
        <DatePicker
          value={dayjs(date)}
          onChange={(d) => d && setDate(d.format('YYYY-MM-DD'))}
        />
        <div style={{ flex: 1 }} />
        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          loading={generating}
          onClick={handleGenerate}
        >
          ブリーフィング生成
        </Button>
      </div>

      <Spin spinning={loading}>
        {briefings.length === 0 ? (
          <Empty
            description="この日のブリーフィングはまだありません"
            style={{ marginTop: 80 }}
          />
        ) : (
          <Row gutter={[16, 16]}>
            {briefings.map((b) => (
              <Col xs={24} lg={12} key={b.category}>
                <div className="briefing-card">
                  <div
                    className="briefing-header"
                    style={{ background: CATEGORY_GRADIENT[b.category] || 'var(--gradient-primary)' }}
                  >
                    {b.category}
                  </div>
                  <div className="briefing-body" dangerouslySetInnerHTML={renderBriefingBody(b.content)} />
                </div>
              </Col>
            ))}
          </Row>
        )}
      </Spin>
    </div>
  )
}
