import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Sidebar from '../Sidebar'

describe('Sidebar', () => {
  it('renders all top-level nav entries', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} />
      </MemoryRouter>
    )
    // Spot-check the labels we know should appear; locks in nav presence
    // ahead of any layout refactor.
    expect(screen.getByText('All Articles')).toBeInTheDocument()
    expect(screen.getByText('Briefing')).toBeInTheDocument()
    expect(screen.getByText('Chat')).toBeInTheDocument()
    expect(screen.getByText('Sources')).toBeInTheDocument()
  })

  it('renders category entries', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} />
      </MemoryRouter>
    )
    expect(screen.getByText('テクノロジー')).toBeInTheDocument()
    expect(screen.getByText('経済・ビジネス')).toBeInTheDocument()
  })
})
