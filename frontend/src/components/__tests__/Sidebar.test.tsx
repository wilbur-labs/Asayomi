import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Sidebar from '../Sidebar'

describe('Sidebar', () => {
  it('renders all top-level nav entries in Japanese', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} />
      </MemoryRouter>
    )
    expect(screen.getByText('記事一覧')).toBeInTheDocument()
    expect(screen.getByText('ブリーフィング')).toBeInTheDocument()
    expect(screen.getByText('AI チャット')).toBeInTheDocument()
    expect(screen.getByText('ソース管理')).toBeInTheDocument()
  })

  it('does NOT render per-category nav entries (tag filter on ArticlesPage now)', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} />
      </MemoryRouter>
    )
    expect(screen.queryByText('テクノロジー')).not.toBeInTheDocument()
    expect(screen.queryByText('経済・ビジネス')).not.toBeInTheDocument()
  })
})
