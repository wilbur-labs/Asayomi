import { useEffect, useState } from 'react'
import { Table, Switch, Tag, Typography, message, Spin } from 'antd'
import { DatabaseOutlined } from '@ant-design/icons'
import { getSources, toggleSource, Source } from '../services/api'

const { Title, Text } = Typography

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)

  const fetch = () =>
    getSources()
      .then((r) => setSources(r.data.sources))
      .finally(() => setLoading(false))

  useEffect(() => {
    fetch()
  }, [])

  const handleToggle = async (name: string, enabled: boolean) => {
    try {
      await toggleSource(name, enabled)
      message.success(`${name} を${enabled ? '有効化' : '無効化'}しました`)
      fetch()
    } catch {
      message.error('切替に失敗しました')
    }
  }

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name', render: (v: string) => <Text strong>{v}</Text> },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (v: string) => <Tag color="blue">{v}</Tag>,
    },
    {
      title: 'Lang',
      dataIndex: 'language',
      key: 'language',
      render: (v: string) => (
        <Tag color={v === 'en' ? 'purple' : 'green'}>{v.toUpperCase()}</Tag>
      ),
    },
    { title: 'Articles', dataIndex: 'count', key: 'count' },
    {
      title: 'Latest',
      dataIndex: 'latest_collected_at',
      key: 'latest_collected_at',
      render: (v: string | null) => (v ? new Date(v).toLocaleString('ja-JP') : '-'),
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      render: (v: string) => (
        <a href={v} target="_blank" rel="noopener" style={{ fontSize: 12 }}>
          {v.length > 40 ? v.slice(0, 40) + '…' : v}
        </a>
      ),
    },
    {
      title: 'Enabled',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled: boolean, row: Source) => (
        <Switch checked={enabled} onChange={(v) => handleToggle(row.name, v)} />
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
          <DatabaseOutlined style={{ marginRight: 8, color: '#0891b2' }} />
          Data Sources
        </Title>
        <Text type="secondary">RSS / Web ソースの管理と健全性確認</Text>
      </div>
      <Spin spinning={loading}>
        <div
          style={{
            background: 'var(--card-bg, #fff)',
            borderRadius: 12,
            padding: 8,
            boxShadow: 'var(--shadow-card)',
          }}
        >
          <Table
            rowKey="name"
            dataSource={sources}
            columns={columns}
            pagination={false}
            size="middle"
          />
        </div>
      </Spin>
    </div>
  )
}
