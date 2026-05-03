import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Header } from '../components/Header'

describe('Header Component', () => {
  it('renders progress title correctly', () => {
    render(
      <Header
        title="Test Title"
      />
    )
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('calls onBack when back button is clicked', () => {
    const onBack = vi.fn()
    render(
      <Header
        title="Title"
        onBack={onBack}
      />
    )
    const backBtn = screen.getByRole('button', { name: /Назад/i })
    backBtn.click()
    expect(onBack).toHaveBeenCalled()
  })
})
