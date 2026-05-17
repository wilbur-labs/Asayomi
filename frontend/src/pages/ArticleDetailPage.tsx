import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  Tag,
  Typography,
  Space,
  Button,
  Spin,
  Empty,
  Divider,
  message,
  Tooltip,
} from 'antd'
import {
  ArrowLeftOutlined,
  LinkOutlined,
  StarOutlined,
  StarFilled,
  ClockCircleOutlined,
  ReadOutlined,
  CheckCircleOutlined,
  FireOutlined,
} from '@ant-design/icons'
import {
  getArticle,
  getRelatedArticles,
  toggleFavorite,
  markRead,
  ArticleDetail,
  Article,
} from '../services/api'

const { Title, Paragraph, Text } = Typography

const catClass = (cat: string) => {
  const map: Record<string, string> = {
    総合: 'cat-総合',
    テクノロジー: 'cat-テクノロジー',
    '経済・ビジネス': 'cat-経済ビジネス',
    国際: 'cat-国際',
  }
  return map[cat] || ''
}

function formatDate(iso: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [related, setRelated] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      getArticle(Number(id)).then((r) => r.data),
      getRelatedArticles(Number(id), 5).then((r) => r.data.related),
    ])
      .then(([a, r]) => {
        setArticle(a)
        setRelated(r)
        // 詳細を開いた時点で既読に
        if (!a.is_read) {
          markRead(a.id).catch(() => {})
        }
      })
      .catch(() => message.error('記事の取得に失敗しました'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!article) {
    return <Empty description="記事が見つかりません" style={{ marginTop: 80 }} />
  }

  const handleFavorite = async () => {
    try {
      const res = await toggleFavorite(article.id)
      setArticle({ ...article, is_favorite: res.data.is_favorite })
    } catch {
      message.error('操作に失敗しました')
    }
  }

  return (
    <div style={{ maxWidth: 880, margin: '0 auto' }}>
      <Button
        type="text"
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate(-1)}
        style={{ marginBottom: 12 }}
      >
        一覧に戻る
      </Button>

      <article
        className="article-card"
        style={{ padding: '28px 32px', marginBottom: 24 }}
      >
        {/* メタ情報 */}
        <Space wrap size={8} style={{ marginBottom: 12 }}>
          <Tag className={catClass(article.category)} style={{ borderRadius: 4, fontWeight: 500 }}>
            {article.category}
          </Tag>
          <Tag bordered={false} color="default" style={{ borderRadius: 4 }}>
            {article.source}
          </Tag>
          {article.language === 'en' && (
            <Tag color="purple" bordered={false} style={{ borderRadius: 4 }}>
              EN→JA
            </Tag>
          )}
          <Text type="secondary" style={{ fontSize: 12 }}>
            <ClockCircleOutlined style={{ marginRight: 4 }} />
            {formatDate(article.published_at || article.collected_at)}
          </Text>
          {article.reading_minutes && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              <ReadOutlined style={{ marginRight: 4 }} />
              約 {article.reading_minutes} 分で読める
            </Text>
          )}
          {article.importance_score > 0 && (
            <Tooltip title={`重要度 ${article.importance_score.toFixed(1)} / 10`}>
              <Tag bordered={false} color="orange" style={{ borderRadius: 4 }}>
                <FireOutlined /> {article.importance_score.toFixed(1)}
              </Tag>
            </Tooltip>
          )}
        </Space>

        <Title level={2} style={{ marginTop: 0, marginBottom: 8, lineHeight: 1.4 }}>
          {article.title}
        </Title>

        {article.original_title && article.language === 'en' && article.original_title !== article.title && (
          <Text type="secondary" italic style={{ display: 'block', marginBottom: 16 }}>
            原題: {article.original_title}
          </Text>
        )}

        {/* アクション */}
        <Space style={{ marginBottom: 20 }}>
          <Button
            icon={
              article.is_favorite ? (
                <StarFilled style={{ color: '#f59e0b' }} />
              ) : (
                <StarOutlined />
              )
            }
            onClick={handleFavorite}
          >
            {article.is_favorite ? 'お気に入り済み' : 'お気に入り'}
          </Button>
          <Button type="primary" icon={<LinkOutlined />} href={article.url} target="_blank">
            元記事を開く
          </Button>
          {article.is_read && (
            <Tag color="default" icon={<CheckCircleOutlined />}>
              既読
            </Tag>
          )}
        </Space>

        {/* メイン画像 */}
        {article.image_url && (
          <div
            style={{
              borderRadius: 12,
              overflow: 'hidden',
              marginBottom: 24,
              background: 'var(--tag-bg, #f3f4f6)',
            }}
          >
            <img
              src={article.image_url}
              alt=""
              loading="lazy"
              referrerPolicy="no-referrer"
              onError={(e) => {
                ;(e.currentTarget.parentElement as HTMLElement).style.display = 'none'
              }}
              style={{ width: '100%', display: 'block', maxHeight: 420, objectFit: 'cover' }}
            />
          </div>
        )}

        {/* 要約 */}
        {article.summary && (
          <div
            style={{
              padding: '16px 20px',
              background: 'var(--summary-bg, #f8fafc)',
              borderLeft: '4px solid var(--accent, #667eea)',
              borderRadius: 6,
              marginBottom: 24,
            }}
          >
            <Text strong style={{ display: 'block', marginBottom: 8, fontSize: 13, color: 'var(--accent, #667eea)' }}>
              AI 要約
            </Text>
            <Text style={{ fontSize: 15, lineHeight: 1.7 }}>{article.summary}</Text>
          </div>
        )}

        {/* 要点 */}
        {article.key_points && article.key_points.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <Text strong style={{ display: 'block', marginBottom: 12, fontSize: 14 }}>
              📌 要点
            </Text>
            <ul style={{ paddingLeft: 20, margin: 0, lineHeight: 1.8 }}>
              {article.key_points.map((p, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  {p}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* タグ */}
        {article.tags.length > 0 && (
          <Space size={4} wrap style={{ marginBottom: 20 }}>
            {article.tags.map((t) => (
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

        <Divider />

        {/* 全文 */}
        {article.full_content ? (
          <div>
            <Text strong style={{ display: 'block', marginBottom: 12, fontSize: 14 }}>
              📖 本文
            </Text>
            <Paragraph
              style={{
                whiteSpace: 'pre-wrap',
                lineHeight: 1.85,
                fontSize: 15,
                color: 'var(--body-color, #374151)',
              }}
            >
              {article.full_content}
            </Paragraph>
          </div>
        ) : article.original_content ? (
          <Paragraph style={{ lineHeight: 1.8, fontSize: 14, color: 'var(--text-secondary, #6b7280)' }}>
            {article.original_content}
          </Paragraph>
        ) : (
          <Text type="secondary">本文を取得できませんでした。元記事を直接ご覧ください。</Text>
        )}
      </article>

      {/* 同事件の他ソース */}
      {article.siblings && article.siblings.length > 0 && (
        <div className="article-card" style={{ padding: 20, marginBottom: 24 }}>
          <Text strong style={{ display: 'block', marginBottom: 12 }}>
            🔁 同じ事件の他ソース報道（{article.siblings.length}）
          </Text>
          <Space direction="vertical" size={6} style={{ width: '100%' }}>
            {article.siblings.map((s) => (
              <div key={s.id}>
                <Tag bordered={false}>{s.source}</Tag>
                <Link to={`/articles/${s.id}`} style={{ marginLeft: 4 }}>
                  {s.title}
                </Link>
              </div>
            ))}
          </Space>
        </div>
      )}

      {/* 関連記事 */}
      {related.length > 0 && (
        <div className="article-card" style={{ padding: 20 }}>
          <Text strong style={{ display: 'block', marginBottom: 12 }}>
            🧭 関連記事
          </Text>
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            {related.map((r) => (
              <Link
                key={r.id}
                to={`/articles/${r.id}`}
                style={{
                  display: 'flex',
                  gap: 12,
                  textDecoration: 'none',
                  color: 'inherit',
                  alignItems: 'flex-start',
                }}
              >
                {r.image_url && (
                  <img
                    src={r.image_url}
                    referrerPolicy="no-referrer"
                    onError={(e) => {
                      ;(e.currentTarget as HTMLElement).style.display = 'none'
                    }}
                    style={{
                      width: 80,
                      height: 60,
                      objectFit: 'cover',
                      borderRadius: 6,
                      flex: '0 0 80px',
                    }}
                  />
                )}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Tag className={catClass(r.category)} style={{ borderRadius: 4, fontSize: 11 }}>
                    {r.category}
                  </Tag>
                  <Text strong style={{ display: 'block', marginTop: 4 }}>
                    {r.title}
                  </Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {r.source} · {formatDate(r.published_at || r.collected_at)}
                  </Text>
                </div>
              </Link>
            ))}
          </Space>
        </div>
      )}
    </div>
  )
}
