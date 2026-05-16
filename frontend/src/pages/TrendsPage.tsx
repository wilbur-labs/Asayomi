import { useEffect, useState } from 'react'
import { Card, Row, Col, Tag, Spin, Typography, Segmented } from 'antd'
import { LineChartOutlined } from '@ant-design/icons'
import { getTrendingTags, getTimeline } from '../services/api'

const { Title, Text } = Typography

const CAT_COLORS: Record<string, string> = {
  総合: '#4f46e5',
  テクノロジー: '#0891b2',
  '経済・ビジネス': '#f59e0b',
  国際: '#db2777',
}

export default function TrendsPage() {
  const [days, setDays] = useState(7)
  const [tags, setTags] = useState<{ tag: string; count: number }[]>([])
  const [timeline, setTimeline] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([getTrendingTags(days, 30), getTimeline(days)])
      .then(([t, tl]) => {
        setTags(t.data.tags)
        setTimeline(tl.data.timeline)
      })
      .finally(() => setLoading(false))
  }, [days])

  const maxCount = Math.max(1, ...tags.map((t) => t.count))
  const tagSize = (count: number) => 12 + (count / maxCount) * 14

  // タイムラインの最大値（バー高さの正規化）
  const allCats = ['総合', 'テクノロジー', '経済・ビジネス', '国際']
  const dayMax = Math.max(
    1,
    ...timeline.map((d) => allCats.reduce((s, c) => s + (d[c] || 0), 0))
  )

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <LineChartOutlined style={{ marginRight: 8, color: '#10b981' }} />
          トレンド
        </Title>
        <Text type="secondary">タグ頻度とカテゴリ別の収集量推移</Text>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Segmented
          value={days}
          onChange={(v) => setDays(Number(v))}
          options={[
            { label: '7日', value: 7 },
            { label: '14日', value: 14 },
            { label: '30日', value: 30 },
          ]}
        />
      </div>

      <Spin spinning={loading}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Card title="🏷️ Trending Tags（タグクラウド）" style={{ boxShadow: 'var(--shadow-card)' }}>
              {tags.length === 0 ? (
                <Text type="secondary">タグデータがありません（AI処理が必要）</Text>
              ) : (
                <div style={{ lineHeight: 2.5 }}>
                  {tags.map((t) => (
                    <Tag
                      key={t.tag}
                      style={{
                        fontSize: tagSize(t.count),
                        padding: '4px 10px',
                        margin: '2px',
                        background: 'var(--gradient-primary)',
                        color: '#fff',
                        border: 'none',
                      }}
                      title={`${t.count} 件`}
                    >
                      {t.tag}
                    </Tag>
                  ))}
                </div>
              )}
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card title="📈 Daily Volume（日別記事数）" style={{ boxShadow: 'var(--shadow-card)' }}>
              {timeline.length === 0 ? (
                <Text type="secondary">データがありません</Text>
              ) : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height: 220, padding: '8px 0' }}>
                  {timeline.map((d) => {
                    const total = allCats.reduce((s, c) => s + (d[c] || 0), 0)
                    return (
                      <div
                        key={d.date}
                        style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}
                        title={`${d.date}: ${total} 件`}
                      >
                        <div
                          style={{
                            width: '100%',
                            display: 'flex',
                            flexDirection: 'column-reverse',
                            height: `${(total / dayMax) * 180}px`,
                            borderRadius: 4,
                            overflow: 'hidden',
                            background: 'var(--tag-bg, #f3f4f6)',
                          }}
                        >
                          {allCats.map((cat) =>
                            d[cat] ? (
                              <div
                                key={cat}
                                style={{
                                  background: CAT_COLORS[cat],
                                  height: `${(d[cat] / total) * 100}%`,
                                }}
                              />
                            ) : null
                          )}
                        </div>
                        <span style={{ fontSize: 10, color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                          {d.date.slice(5)}
                        </span>
                      </div>
                    )
                  })}
                </div>
              )}
              <div style={{ marginTop: 12, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {allCats.map((c) => (
                  <span key={c} style={{ fontSize: 12, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                    <span style={{ width: 10, height: 10, background: CAT_COLORS[c], borderRadius: 2 }} />
                    {c}
                  </span>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}
