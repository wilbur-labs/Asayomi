import { useEffect, useState } from 'react'
import { Row, Col, Spin, Typography, Progress, Card } from 'antd'
import {
  BarChartOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { getStats } from '../services/api'

const { Title, Text } = Typography

interface Stats {
  total: number
  processed: number
  unprocessed: number
  by_category: Record<string, number>
  by_source: Record<string, number>
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
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats()
      .then((res) => setStats(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin style={{ display: 'block', marginTop: 80 }} />
  if (!stats) return null

  const processRate = stats.total > 0 ? (stats.processed / stats.total) * 100 : 0
  const sourceMax = Math.max(1, ...Object.values(stats.by_source))
  const categoryMax = Math.max(1, ...Object.values(stats.by_category))

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <BarChartOutlined style={{ marginRight: 8, color: '#10b981' }} />
          統計ダッシュボード
        </Title>
        <Text type="secondary">記事収集・処理状況の可視化</Text>
      </div>

      {/* メトリクスカード */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[0] }}>
            <DatabaseOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">総記事数</div>
            <div className="stat-value">{stats.total.toLocaleString()}</div>
          </div>
        </Col>
        <Col xs={24} sm={8}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[1] }}>
            <CheckCircleOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">AI処理済み</div>
            <div className="stat-value">{stats.processed.toLocaleString()}</div>
          </div>
        </Col>
        <Col xs={24} sm={8}>
          <div className="stat-card" style={{ background: CARD_GRADIENTS[2] }}>
            <ClockCircleOutlined style={{ fontSize: 24, marginBottom: 12 }} />
            <div className="stat-label">処理待ち</div>
            <div className="stat-value">{stats.unprocessed.toLocaleString()}</div>
          </div>
        </Col>
      </Row>

      {/* 処理進捗 */}
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
        {/* カテゴリ別 */}
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
                  <Progress
                    percent={(v / categoryMax) * 100}
                    showInfo={false}
                    strokeColor={CATEGORY_COLORS[k] || '#667eea'}
                  />
                </div>
              ))
            )}
          </Card>
        </Col>

        {/* ソース別 */}
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
                  <Progress
                    percent={(v / sourceMax) * 100}
                    showInfo={false}
                    strokeColor="#4f46e5"
                  />
                </div>
              ))}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
