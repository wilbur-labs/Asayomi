import { useEffect, useState } from 'react'
import { Row, Col, Spin, Typography, Progress, Card, Button, Space, Tag } from 'antd'
import {
  BarChartOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import { getStats, getUsage } from '../services/api'

const { Title, Text } = Typography

interface Stats {
  total: number
  processed: number
  unprocessed: number
  by_category: Record<string, number>
  by_source: Record<string, number>
}

interface Usage {
  total_calls: number
  total_tokens: number
  total_cost_usd: number
  by_operation: Record<string, { count: number; tokens: number; cost: number }>
}

const CARD_GRADIENTS = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
  'linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)',
]

const CATEGORY_COLORS: Record<string, string> = {
  総合: '#4f46e5',
  テクノロジー: '#0891b2',
  '経済・ビジネス': '#f59e0b',
  国際: '#db2777',
}

export default function StatsPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [usage, setUsage] = useState<Usage | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getStats(), getUsage(30)])
      .then(([s, u]) => {
        setStats(s.data)
        setUsage(u.data as any)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin style={{ display: 'block', marginTop: 80 }} />
  if (!stats) return null

  const processRate = stats.total > 0 ? (stats.processed / stats.total) * 100 : 0
  const sourceMax = Math.max(1, ...Object.values(stats.by_source))
  const categoryMax = Math.max(1, ...Object.values(stats.by_category))

  return (
    <div>
      <div
        style={{
          marginBottom: 24,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-end',
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div>
          <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
            <BarChartOutlined style={{ marginRight: 8, color: '#10b981' }} />
            Stats
          </Title>
          <Text type="secondary">記事収集・AI処理・API用量の可視化</Text>
        </div>
        <Space>
          <Button
            icon={<DownloadOutlined />}
            onClick={() => window.open('/api/v1/export/articles.json', '_blank')}
          >
            JSON
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={() => window.open('/api/v1/export/articles.csv', '_blank')}
          >
            CSV
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[0] }}>
            <DatabaseOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">総記事数</div>
            <div className="stat-value">{stats.total.toLocaleString()}</div>
          </div>
        </Col>
        <Col xs={24} sm={6}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[1] }}>
            <CheckCircleOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">AI処理済み</div>
            <div className="stat-value">{stats.processed.toLocaleString()}</div>
          </div>
        </Col>
        <Col xs={24} sm={6}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[2] }}>
            <ClockCircleOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">処理待ち</div>
            <div className="stat-value">{stats.unprocessed.toLocaleString()}</div>
          </div>
        </Col>
        <Col xs={24} sm={6}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[3] }}>
            <DollarOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">API コスト (30日)</div>
            <div className="stat-value">${(usage?.total_cost_usd ?? 0).toFixed(2)}</div>
          </div>
        </Col>
      </Row>

      <Card style={{ marginBottom: 16, boxShadow: 'var(--shadow-card)' }}>
        <Text strong style={{ display: 'block', marginBottom: 12 }}>
          AI処理進捗
        </Text>
        <Progress
          percent={Number(processRate.toFixed(1))}
          strokeColor={{ '0%': '#667eea', '100%': '#764ba2' }}
          format={(p) => `${p}%`}
        />
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="📁 カテゴリ別" style={{ boxShadow: 'var(--shadow-card)' }}>
            {Object.keys(stats.by_category).length === 0 ? (
              <Text type="secondary">AI処理後に表示されます</Text>
            ) : (
              Object.entries(stats.by_category).map(([k, v]) => (
                <div key={k} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text strong style={{ color: CATEGORY_COLORS[k] || '#374151' }}>
                      {k}
                    </Text>
                    <Text>{v} 件</Text>
                  </div>
                  <Progress percent={(v / categoryMax) * 100} showInfo={false} strokeColor={CATEGORY_COLORS[k] || '#667eea'} />
                </div>
              ))
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="📰 ソース別" style={{ boxShadow: 'var(--shadow-card)' }}>
            {Object.entries(stats.by_source)
              .sort(([, a], [, b]) => b - a)
              .map(([k, v]) => (
                <div key={k} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text>{k}</Text>
                    <Text strong>{v} 件</Text>
                  </div>
                  <Progress percent={(v / sourceMax) * 100} showInfo={false} strokeColor="#4f46e5" />
                </div>
              ))}
          </Card>
        </Col>

        {usage && Object.keys(usage.by_operation).length > 0 && (
          <Col xs={24}>
            <Card title="💸 API用量（直近30日）" style={{ boxShadow: 'var(--shadow-card)' }}>
              <Space size={24} wrap>
                <Text>呼び出し: <Text strong>{usage.total_calls}</Text></Text>
                <Text>トークン: <Text strong>{usage.total_tokens.toLocaleString()}</Text></Text>
                <Text>推定コスト: <Text strong>${usage.total_cost_usd.toFixed(4)}</Text></Text>
              </Space>
              <div style={{ marginTop: 16 }}>
                {Object.entries(usage.by_operation).map(([op, data]) => (
                  <Tag key={op} color="blue" style={{ marginBottom: 6, padding: '4px 10px' }}>
                    {op}: {data.count} 回 / {data.tokens.toLocaleString()} tok / ${data.cost.toFixed(4)}
                  </Tag>
                ))}
              </div>
            </Card>
          </Col>
        )}
      </Row>
    </div>
  )
}
