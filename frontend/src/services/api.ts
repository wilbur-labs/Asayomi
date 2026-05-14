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

export interface Source {
  name: string
  url: string
  category: string
  language: string
  enabled: boolean
  count: number
  latest_collected_at: string | null
}

export const getArticles = (params?: {
  category?: string
  source?: string
  favorite_only?: boolean
  unread_only?: boolean
  limit?: number
  offset?: number
}) => api.get<{ total: number; articles: Article[] }>('/articles', { params })

export const searchArticles = (q: string, limit = 50) =>
  api.get<{ total: number; articles: Article[] }>('/search', { params: { q, limit } })

export const toggleFavorite = (id: number) =>
  api.post<{ id: number; is_favorite: boolean }>(`/articles/${id}/favorite`)

export const markRead = (id: number) => api.post(`/articles/${id}/read`)
export const markUnread = (id: number) => api.post(`/articles/${id}/unread`)

export const getBriefings = (date?: string) =>
  api.get<{ date: string; briefings: { id: number; category: string; content: string }[] }>(
    '/briefings',
    { params: { date } }
  )

export const getStats = () => api.get('/stats')

export const getSources = () => api.get<{ sources: Source[] }>('/sources')
export const toggleSource = (name: string, enabled: boolean) =>
  api.post(`/sources/${encodeURIComponent(name)}/toggle`, { enabled })

export const triggerCollect = () => api.post('/system/collect')
export const triggerProcess = () => api.post('/system/process')
export const triggerDedupe = () => api.post('/system/dedupe')
export const triggerBriefing = () => api.post('/system/briefing')
export const triggerWeekly = () => api.post('/system/briefing/weekly')
export const triggerMonthly = () => api.post('/system/briefing/monthly')
export const triggerNotify = () => api.post('/system/notify')
export const triggerRunAll = () => api.post('/system/run-all')
