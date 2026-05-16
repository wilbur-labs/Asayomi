import { useEffect, useState } from 'react'
import {
  DatePicker,
  Empty,
  Spin,
  Typography,
  Row,
  Col,
  Button,
  message,
  Segmented,
  Tooltip,
} from 'antd'
import {
  FileTextOutlined,
  ThunderboltOutlined,
  MailOutlined,
  ExportOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import {
  getBriefings,
  triggerBriefing,
  triggerWeekly,
  triggerMonthly,
  triggerNotify,
} from '../services/api'

const { Title, Text } = Typography

type Mode = 'daily' | 'weekly' | 'monthly'

const CATEGORY_GRADIENT: Record<string, string> = {
  総合: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  テクノロジー: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  '経済・ビジネス': 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
  国際: 'linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)',
}

function renderBriefingBody(content: string) {
  const html = content
    .replace(/^## .+$/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(https?:\/\/[^\s)]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
  return { __html: html }
}

export default function BriefingPage() {
  const [mode, setMode] = useState<Mode>('daily')
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [month, setMonth] = useState(dayjs().format('YYYY-MM'))
  const [briefings, setBriefings] = useState<{ category: string; content: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)

  const targetLabel = () => {
    if (mode === 'daily') return date
    if (mode === 'weekly') return `weekly-${date}`
    return `monthly-${month}`
  }

  const fetchBriefings = () => {
    setLoading(true)
    getBriefings(targetLabel())
      .then((res) => setBriefings(res.data.briefings))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchBriefings()
  }, [mode, date, month])

  const handleGenerate = async () => {
    setBusy(true)
    try {
      const res =
        mode === 'daily'
          ? await triggerBriefing()
          : mode === 'weekly'
            ? await triggerWeekly()
            : await triggerMonthly()
      message.success(res.data.message)
      fetchBriefings()
    } catch {
      message.error('生成に失敗しました')
    } finally {
      setBusy(false)
    }
  }

  const handleNotify = async () => {
    setBusy(true)
    try {
      const res = await triggerNotify()
      const ch = res.data?.channels || {}
      const ok = Object.values(ch).filter(Boolean).length
      message.success(`通知送信: ${ok} チャンネル成功`)
    } catch {
      message.error('通知に失敗しました')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <FileTextOutlined style={{ marginRight: 8, color: '#4f46e5' }} />
          ブリーフィング
        </Title>
        <Text type="secondary">日次・週次・月次のカテゴリ別まとめ</Text>
      </div>

      <div
        style={{
          background: 'var(--card-bg, #fff)',
          padding: 16,
          borderRadius: 12,
          marginBottom: 16,
          boxShadow: 'var(--shadow-card)',
          display: 'flex',
          flexWrap: 'wrap',
          gap: 12,
          alignItems: 'center',
        }}
      >
        <Segmented
          value={mode}
          onChange={(v) => setMode(v as Mode)}
          options={[
            { label: '日次', value: 'daily' },
            { label: '週次', value: 'weekly' },
            { label: '月次', value: 'monthly' },
          ]}
        />
        {mode !== 'monthly' ? (
          <DatePicker
            value={dayjs(date)}
            onChange={(d) => d && setDate(d.format('YYYY-MM-DD'))}
          />
        ) : (
          <DatePicker
            picker="month"
            value={dayjs(month)}
            onChange={(d) => d && setMonth(d.format('YYYY-MM'))}
          />
        )}
        <div style={{ flex: 1 }} />
        <Tooltip title="RSS フィード（XML）を新しいタブで開く">
          <Button icon={<ExportOutlined />} onClick={() => window.open('/api/v1/feed/rss.xml', '_blank')}>
            RSS
          </Button>
        </Tooltip>
        <Button icon={<MailOutlined />} loading={busy} onClick={handleNotify}>
          通知送信
        </Button>
        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          loading={busy}
          onClick={handleGenerate}
        >
          生成
        </Button>
      </div>

      <Spin spinning={loading}>
        {briefings.length === 0 ? (
          <Empty
            description="この期間のブリーフィングはまだありません"
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
