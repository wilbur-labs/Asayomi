import { useEffect, useState } from 'react'
import { Card, Statistic, Row, Col, Spin } from 'antd'
import { getStats } from '../services/api'

export default function StatsPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats().then(res => setStats(res.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin />
  if (!stats) return null

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}><Card><Statistic title="総記事数" value={stats.total} /></Card></Col>
        <Col span={8}><Card><Statistic title="処理済み" value={stats.processed} /></Card></Col>
        <Col span={8}><Card><Statistic title="未処理" value={stats.unprocessed} /></Card></Col>
      </Row>
      <Row gutter={16}>
        <Col span={12}>
          <Card title="カテゴリ別">
            {Object.entries(stats.by_category || {}).map(([k, v]) => (
              <p key={k}>{k}: {v as number} 件</p>
            ))}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="ソース別">
            {Object.entries(stats.by_source || {}).map(([k, v]) => (
              <p key={k}>{k}: {v as number} 件</p>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
