import { useEffect, useState, useCallback } from 'react'
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
  Pagination,
  Switch,
} from 'antd'
import {
  LinkOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
  FireOutlined,
  ClockCircleOutlined,
  StarOutlined,
  StarFilled,
  CheckOutlined,
} from '@ant-design/icons'
import {
  getArticles,
  searchArticles,
  toggleFavorite,
  markRead,
  Article,
  triggerCollect,
  triggerProcess,
} from '../services/api'

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

const PAGE_SIZE = 20

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState<string>('')
  const [keyword, setKeyword] = useState<string>('')
  const [searchMode, setSearchMode] = useState(false)
  const [favoriteOnly, setFavoriteOnly] = useState(false)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  const fetchArticles = useCallback(async () => {
    setLoading(true)
    try {
      if (searchMode && keyword) {
        const res = await searchArticles(keyword)
        setArticles(res.data.articles)
        setTotal(res.data.total)
      } else {
        const params: any = { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE }
        if (category) params.category = category
        if (favoriteOnly) params.favorite_only = true
        if (unreadOnly) params.unread_only = true
        const res = await getArticles(params)
        setArticles(res.data.articles)
        setTotal(res.data.total)
      }
    } finally {
      setLoading(false)
    }
  }, [category, page, favoriteOnly, unreadOnly, searchMode, keyword])

  useEffect(() => {
    fetchArticles()
  }, [fetchArticles])

  // フィルタ変更時はページを 1 に戻す
  useEffect(() => {
    setPage(1)
  }, [category, favoriteOnly, unreadOnly])

  const handleSearch = (q: string) => {
    if (q.trim()) {
      setSearchMode(true)
      setKeyword(q)
    } else {
      setSearchMode(false)
      setKeyword('')
    }
  }

  const handleFavorite = async (a: Article) => {
    try {
      const res = await toggleFavorite(a.id)
      setArticles((arr) =>
        arr.map((x) => (x.id === a.id ? { ...x, is_favorite: res.data.is_favorite } : x))
      )
    } catch {
      message.error('操作に失敗しました')
    }
  }

  const handleRead = async (a: Article) => {
    if (a.is_read) return
    try {
      await markRead(a.id)
      setArticles((arr) => arr.map((x) => (x.id === a.id ? { ...x, is_read: true } : x)))
    } catch {
      // silent
    }
  }

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
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <FireOutlined style={{ marginRight: 8, color: '#f59e0b' }} />
          Articles
        </Title>
        <Text type="secondary">日本ニュース · 自動収集 · AI 要約</Text>
      </div>

      {/* ツールバー */}
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
        <Select
          value={category || '全て'}
          onChange={(v) => setCategory(v === '全て' ? '' : v)}
          options={CATEGORIES.map((c) => ({ value: c, label: c }))}
          style={{ width: 160 }}
        />
        <Search
          placeholder="全文検索（FTS5）…"
          allowClear
          enterButton
          onSearch={handleSearch}
          style={{ flex: 1, minWidth: 200, maxWidth: 360 }}
        />
        <Space>
          <Switch
            size="small"
            checked={favoriteOnly}
            onChange={setFavoriteOnly}
            checkedChildren={<StarFilled />}
            unCheckedChildren={<StarOutlined />}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            お気に入りのみ
          </Text>
        </Space>
        <Space>
          <Switch size="small" checked={unreadOnly} onChange={setUnreadOnly} />
          <Text type="secondary" style={{ fontSize: 12 }}>
            未読のみ
          </Text>
        </Space>
        <div style={{ flex: 1 }} />
        <Text type="secondary">{total} 件</Text>
        <Button icon={<ReloadOutlined />} loading={actionLoading} onClick={handleCollect}>
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

      <Spin spinning={loading}>
        {articles.length === 0 ? (
          <Empty description="記事がありません" style={{ marginTop: 80 }} />
        ) : (
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            {articles.map((a) => (
              <div
                key={a.id}
                className="article-card"
                style={{
                  padding: 20,
                  opacity: a.is_read ? 0.65 : 1,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}
                    >
                      <Tag
                        className={catClass(a.category)}
                        style={{ borderRadius: 4, fontWeight: 500 }}
                      >
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
                      {a.is_read && (
                        <Tag color="default" bordered={false} icon={<CheckOutlined />}>
                          既読
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
                      onClick={() => handleRead(a)}
                      style={{
                        fontSize: 16,
                        fontWeight: 600,
                        color: 'var(--title-color, #1a202c)',
                        textDecoration: 'none',
                        lineHeight: 1.5,
                        display: 'block',
                        marginBottom: 6,
                      }}
                    >
                      {a.title}
                      <LinkOutlined style={{ marginLeft: 6, fontSize: 12, opacity: 0.5 }} />
                    </a>
                    {a.original_title && a.language === 'en' && a.original_title !== a.title && (
                      <Text
                        type="secondary"
                        italic
                        style={{ fontSize: 12, display: 'block', marginBottom: 6 }}
                      >
                        原題: {a.original_title}
                      </Text>
                    )}
                    {a.summary && (
                      <Paragraph
                        ellipsis={{ rows: 2 }}
                        style={{ color: 'var(--text-secondary, #6b7280)', marginBottom: 8, fontSize: 13 }}
                      >
                        {a.summary}
                      </Paragraph>
                    )}
                    {a.tags.length > 0 && (
                      <Space size={4} wrap>
                        {a.tags.map((t) => (
                          <Tag
                            key={t}
                            bordered={false}
                            style={{ background: 'var(--tag-bg, #f3f4f6)', color: 'var(--text-secondary, #6b7280)' }}
                          >
                            #{t}
                          </Tag>
                        ))}
                      </Space>
                    )}
                  </div>
                  <Button
                    type="text"
                    icon={
                      a.is_favorite ? (
                        <StarFilled style={{ color: '#f59e0b' }} />
                      ) : (
                        <StarOutlined />
                      )
                    }
                    onClick={() => handleFavorite(a)}
                  />
                </div>
              </div>
            ))}
          </Space>
        )}

        {!searchMode && total > PAGE_SIZE && (
          <div style={{ marginTop: 24, textAlign: 'center' }}>
            <Pagination
              current={page}
              pageSize={PAGE_SIZE}
              total={total}
              onChange={setPage}
              showSizeChanger={false}
            />
          </div>
        )}
      </Spin>
    </div>
  )
}
