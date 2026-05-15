import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'

// Mock the api module before importing the page. The page does data fetches
// in useEffect; without these mocks it would try to hit the real backend.
vi.mock('../../services/api', () => ({
  getArticles: vi.fn().mockResolvedValue({
    data: { total: 0, articles: [] },
  }),
  searchArticles: vi.fn().mockResolvedValue({ data: { total: 0, articles: [] } }),
  toggleFavorite: vi.fn(),
  markRead: vi.fn(),
  triggerCollect: vi.fn(),
  triggerProcess: vi.fn(),
}))

import ArticlesPage from '../ArticlesPage'

describe('ArticlesPage (smoke)', () => {
  it('renders without crashing on empty state', async () => {
    render(
      <MemoryRouter>
        <ArticlesPage />
      </MemoryRouter>
    )
    // Search input is rendered unconditionally; its placeholder is a stable
    // selector that doesn't depend on which category route we're on.
    await waitFor(() => {
      expect(screen.getByPlaceholderText('全文検索…')).toBeInTheDocument()
    })
  })
})
