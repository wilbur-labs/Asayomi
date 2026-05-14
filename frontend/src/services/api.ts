import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export interface Article {
  id: number
  title: string
  original_title: string | null
  url: string
  source: string
  language: string
  category: string
  summary: string | null
  importance_score: number
  tags: string[]
  published_at: string | null
  collected_at: string | null
  is_favorite: boolean
  is_read: boolean
}

export const getArticles = (params?: {
  category?: string
  source?: string
  limit?: number
  offset?: number
}) => api.get<{ total: number; articles: Article[] }>('/articles', { params })

export const getBriefings = (date?: string) =>
  api.get<{ date: string; briefings: { id: number; category: string; content: string }[] }>(
    '/briefings',
    { params: { date } }
  )

export const getStats = () => api.get('/stats')

export const triggerCollect = () => api.post('/system/collect')
export const triggerProcess = () => api.post('/system/process')
export const triggerDedupe = () => api.post('/system/dedupe')
export const triggerRunAll = () => api.post('/system/run-all')
