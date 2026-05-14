import { useEffect, useState } from 'react'
import { Card, DatePicker, Empty, Spin } from 'antd'
import dayjs from 'dayjs'
import { getBriefings } from '../services/api'

export default function BriefingPage() {
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [briefings, setBriefings] = useState<{ category: string; content: string }[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    getBriefings(date)
      .then(res => setBriefings(res.data.briefings))
      .finally(() => setLoading(false))
  }, [date])

  return (
    <div>
      <DatePicker
        value={dayjs(date)}
        onChange={(d) => d && setDate(d.format('YYYY-MM-DD'))}
        style={{ marginBottom: 16 }}
      />
      <Spin spinning={loading}>
        {briefings.length === 0 ? (
          <Empty description="ブリーフィングがありません" />
        ) : (
          briefings.map((b) => (
            <Card key={b.category} title={b.category} style={{ marginBottom: 16 }}>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{b.content}</pre>
            </Card>
          ))
        )}
      </Spin>
    </div>
  )
}
