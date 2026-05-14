import { useEffect, useState } from 'react'
import { Card, Tag, Select, List, Typography, Space, Rate } from 'antd'
import { getArticles, Article } from '../services/api'

const { Text, Link } = Typography
const CATEGORIES = ['全て', '総合', 'テクノロジー', '経済・ビジネス', '国際']

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [category, setCategory] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const fetchArticles = async () => {
    setLoading(true)
    try {
      const params = category ? { category, limit: 50 } : { limit: 50 }
      const res = await getArticles(params)
      setArticles(res.data.articles)
      setTotal(res.data.total)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchArticles() }, [category])

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          value={category || '全て'}
          onChange={(v) => setCategory(v === '全て' ? '' : v)}
          options={CATEGORIES.map(c => ({ value: c, label: c }))}
          style={{ width: 160 }}
        />
        <Text type="secondary">{total} 件</Text>
      </Space>
      <List
        loading={loading}
        dataSource={articles}
        renderItem={(item) => (
          <Card size="small" style={{ marginBottom: 8 }}>
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Space>
                <Link href={item.url} target="_blank">{item.title}</Link>
                <Rate disabled value={item.importance_score / 2} count={5} style={{ fontSize: 12 }} />
              </Space>
              {item.summary && <Text type="secondary">{item.summary}</Text>}
              <Space size={4}>
                <Tag color="blue">{item.source}</Tag>
                <Tag>{item.category}</Tag>
                {item.tags.map(t => <Tag key={t}>{t}</Tag>)}
              </Space>
            </Space>
          </Card>
        )}
      />
    </div>
  )
}
