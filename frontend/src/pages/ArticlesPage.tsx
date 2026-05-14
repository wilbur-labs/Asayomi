import { useEffect, useState } from 'react'
import {
  Tag,
  Select,
  Space,
  Empty,
  Typography,
  Spin,
  Button,
  message,
  Input,
  Tooltip,
} from 'antd'
import {
  LinkOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
  FireOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { getArticles, Article, triggerCollect, triggerProcess } from '../services/api'

const { Title, Text, Paragraph } = Typography
const { Search } = Input

const CATEGORIES = ['全て', '総合', 'テクノロジー', '経済・ビジネス', '国際']

const catClass = (cat: string) => {
  const map: Record<string, string> = {
    総合: 'cat-総合',
    テクノロジー: 'cat-テクノロジー',
    '経済・ビジネス': 'cat-経済ビジネス',
    国際: 'cat-国際',
  }
  return map[cat] || ''
}

function ScoreBars({ score }: { score: number }) {
  const filled = Math.min(5, Math.max(0, Math.round(score / 2)))
  return (
    <Tooltip title={`重要度 ${score.toFixed(1)} / 10`}>
      <span>
        {[1, 2, 3, 4, 5].map((i) => (
          <span key={i} className={`score-bar ${i <= filled ? `active-${filled}` : ''}`} />
        ))}
      </span>
    </Tooltip>
  )
}

function timeAgo(iso: string | null): string {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'たった今'
  if (mins < 60) return `${mins}分前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}時間前`
  const days = Math.floor(hours / 24)
  return `${days}日前`
}

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [category, setCategory] = useState<string>('')
  const [keyword, setKeyword] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  const fetchArticles = async () => {
    setLoading(true)
    try {
      const params: any = { limit: 50 }
      if (category) params.category = category
      const res = await getArticles(params)
      setArticles(res.data.articles)
      setTotal(res.data.total)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchArticles()
  }, [category])

  const filtered = keyword
    ? articles.filter(
        (a) =>
          a.title.toLowerCase().includes(keyword.toLowerCase()) ||
          (a.summary || '').toLowerCase().includes(keyword.toLowerCase())
      )
    : articles

  const handleCollect = async () => {
    setActionLoading(true)
    try {
      const res = await triggerCollect()
      message.success(res.data.message)
      fetchArticles()
    } catch {
      message.error('収集に失敗しました')
    } finally {
      setActionLoading(false)
    }
  }

  const handleProcess = async () => {
    setActionLoading(true)
    try {
      const res = await triggerProcess()
      message.success(res.data.message)
      fetchArticles()
    } catch {
      message.error('AI処理に失敗しました')
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <div>
      {/* ヘッダー */}
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <FireOutlined style={{ marginRight: 8, color: '#f59e0b' }} />
          ニュース一覧
        </Title>
        <Text type="secondary">日本の主要ニュースサイトから最新記事を自動収集</Text>
      </div>

      {/* ツールバー */}
      <div
        style={{
          background: '#fff',
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
        <Select
          value={category || '全て'}
          onChange={(v) => setCategory(v === '全て' ? '' : v)}
          options={CATEGORIES.map((c) => ({ value: c, label: c }))}
          style={{ width: 160 }}
        />
        <Search
          placeholder="キーワード検索…"
          allowClear
          onChange={(e) => setKeyword(e.target.value)}
          style={{ flex: 1, minWidth: 200, maxWidth: 360 }}
        />
        <div style={{ flex: 1 }} />
        <Text type="secondary" style={{ marginRight: 8 }}>
          {filtered.length} / {total} 件
        </Text>
        <Button
          icon={<ReloadOutlined />}
          loading={actionLoading}
          onClick={handleCollect}
        >
          収集
        </Button>
        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          loading={actionLoading}
          onClick={handleProcess}
        >
          AI処理
        </Button>
      </div>

      {/* 記事リスト */}
      <Spin spinning={loading}>
        {filtered.length === 0 ? (
          <Empty description="記事がありません" style={{ marginTop: 80 }} />
        ) : (
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            {filtered.map((a) => (
              <div key={a.id} className="article-card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <Tag className={catClass(a.category)} style={{ borderRadius: 4, fontWeight: 500 }}>
                        {a.category}
                      </Tag>
                      <Tag bordered={false} color="default" style={{ borderRadius: 4 }}>
                        {a.source}
                      </Tag>
                      {a.language === 'en' && (
                        <Tag color="purple" bordered={false} style={{ borderRadius: 4 }}>
                          EN→JA
                        </Tag>
                      )}
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        <ClockCircleOutlined style={{ marginRight: 4 }} />
                        {timeAgo(a.published_at || a.collected_at)}
                      </Text>
                      {a.importance_score > 0 && (
                        <span style={{ marginLeft: 'auto' }}>
                          <ScoreBars score={a.importance_score} />
                        </span>
                      )}
                    </div>
                    <a
                      href={a.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        fontSize: 16,
                        fontWeight: 600,
                        color: '#1a202c',
                        textDecoration: 'none',
                        lineHeight: 1.5,
                        display: 'block',
                        marginBottom: 6,
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = '#4f46e5')}
                      onMouseLeave={(e) => (e.currentTarget.style.color = '#1a202c')}
                    >
                      {a.title}
                      <LinkOutlined style={{ marginLeft: 6, fontSize: 12, opacity: 0.5 }} />
                    </a>
                    {a.summary && (
                      <Paragraph
                        ellipsis={{ rows: 2 }}
                        style={{ color: '#6b7280', marginBottom: 8, fontSize: 13 }}
                      >
                        {a.summary}
                      </Paragraph>
                    )}
                    {a.tags.length > 0 && (
                      <Space size={4} wrap>
                        {a.tags.map((t) => (
                          <Tag key={t} bordered={false} style={{ background: '#f3f4f6', color: '#6b7280' }}>
                            #{t}
                          </Tag>
                        ))}
                      </Space>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </Space>
        )}
      </Spin>
    </div>
  )
}
