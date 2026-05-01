import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Header } from './Header'

describe('Header Component', () => {
  it('renders progress title correctly', () => {
    render(
      <Header
        title="Test Title"
        language="en"
        onToggleLanguage={vi.fn()}
      />
    )
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('calls onBack when back button is clicked', () => {
    const onBack = vi.fn()
    const onToggleLanguage = vi.fn()
    render(
      <Header
        title="Title"
        onBack={onBack}
        language="ru"
        onToggleLanguage={onToggleLanguage}
      />
    )
    const backBtn = screen.getByRole('button', { name: /Назад/i })
    backBtn.click()
    expect(onBack).toHaveBeenCalled()
  })
})
