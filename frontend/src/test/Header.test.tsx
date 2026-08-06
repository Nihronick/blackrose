import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { Header } from '../components/Header'

describe('Header Component', () => {
  it('renders progress title correctly', () => {
    render(
      <MemoryRouter>
        <Header title="Test Title" />
      </MemoryRouter>
    )
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('calls onBack when back button is clicked', () => {
    const onBack = vi.fn()
    render(
      <MemoryRouter>
        <Header title="Title" onBack={onBack} />
      </MemoryRouter>
    )
    const backBtn = screen.getByRole('button', { name: /Назад/i })
    backBtn.click()
    expect(onBack).toHaveBeenCalled()
  })
})
