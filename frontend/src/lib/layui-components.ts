/**
 * W3C Custom Elements wrapping Layui styles for modern, responsive components.
 */

class LayuiButton extends HTMLElement {
  connectedCallback() {
    const type = this.getAttribute('type') || 'default'
    const size = this.getAttribute('size') || 'md'
    const radius = this.hasAttribute('radius')

    const btn = document.createElement('button')
    btn.className = `layui-btn ${
      type === 'primary' ? 'layui-btn-normal' :
      type === 'warm' ? 'layui-btn-warm' :
      type === 'danger' ? 'layui-btn-danger' :
      type === 'disabled' ? 'layui-btn-disabled' :
      type === 'outline' ? 'layui-btn-primary' : 'layui-btn-primary'
    } ${
      size === 'lg' ? 'layui-btn-lg' :
      size === 'sm' ? 'layui-btn-sm' :
      size === 'xs' ? 'layui-btn-xs' : ''
    } ${radius ? 'layui-btn-radius' : ''}`
    
    const customClass = this.getAttribute('class')
    if (customClass) btn.className += ` ${customClass}`
    
    const style = this.getAttribute('style')
    if (style) btn.setAttribute('style', style)

    // Move children to button
    while (this.firstChild) {
      btn.appendChild(this.firstChild)
    }

    this.appendChild(btn)
  }
}

class LayuiBadge extends HTMLElement {
  connectedCallback() {
    const color = this.getAttribute('color') || 'default'
    const rim = this.hasAttribute('rim')

    const span = document.createElement('span')
    span.className = `${rim ? 'layui-badge-rim' : 'layui-badge'} ${
      color === 'green' ? 'layui-bg-green' :
      color === 'blue' ? 'layui-bg-blue' :
      color === 'orange' ? 'layui-bg-orange' :
      color === 'red' ? 'layui-bg-red' :
      color === 'cyan' ? 'layui-bg-cyan' :
      color === 'black' ? 'layui-bg-black' : ''
    }`

    const customClass = this.getAttribute('class')
    if (customClass) span.className += ` ${customClass}`

    while (this.firstChild) {
      span.appendChild(this.firstChild)
    }

    this.appendChild(span)
  }
}

class LayuiCard extends HTMLElement {
  connectedCallback() {
    const title = this.getAttribute('title') || ''

    const card = document.createElement('div')
    card.className = 'layui-card'

    if (title) {
      const header = document.createElement('div')
      header.className = 'layui-card-header'
      header.textContent = title
      card.appendChild(header)
    }

    const body = document.createElement('div')
    body.className = 'layui-card-body'

    while (this.firstChild) {
      body.appendChild(this.firstChild)
    }
    card.appendChild(body)

    const customClass = this.getAttribute('class')
    if (customClass) card.className += ` ${customClass}`

    this.appendChild(card)
  }
}

class LayuiProgress extends HTMLElement {
  static get observedAttributes() {
    return ['percent']
  }

  connectedCallback() {
    this.render()
  }

  attributeChangedCallback() {
    this.render()
  }

  render() {
    this.innerHTML = ''
    const percent = this.getAttribute('percent') || '0%'
    const color = this.getAttribute('color') || 'blue'

    const container = document.createElement('div')
    container.className = 'layui-progress'

    const bar = document.createElement('div')
    bar.className = `layui-progress-bar ${
      color === 'red' ? 'layui-bg-red' :
      color === 'orange' ? 'layui-bg-orange' :
      color === 'green' ? 'layui-bg-green' :
      color === 'cyan' ? 'layui-bg-cyan' : 'layui-bg-blue'
    }`
    bar.style.width = percent
    bar.setAttribute('lay-percent', percent)

    container.appendChild(bar)
    this.appendChild(container)
  }
}

class LayuiTimeline extends HTMLElement {
  connectedCallback() {
    const list = document.createElement('ul')
    list.className = 'layui-timeline'

    const customClass = this.getAttribute('class')
    if (customClass) list.className += ` ${customClass}`

    while (this.firstChild) {
      list.appendChild(this.firstChild)
    }

    this.appendChild(list)
  }
}

class LayuiTimelineItem extends HTMLElement {
  connectedCallback() {
    const time = this.getAttribute('time') || ''
    const title = this.getAttribute('title') || ''

    const item = document.createElement('li')
    item.className = 'layui-timeline-item'

    const icon = document.createElement('i')
    icon.className = 'layui-icon layui-timeline-axis'
    icon.innerHTML = '&#xe63f;' // default dot icon
    item.appendChild(icon)

    const content = document.createElement('div')
    content.className = 'layui-timeline-content layui-text'

    if (time) {
      const timeHeader = document.createElement('h3')
      timeHeader.className = 'layui-timeline-title'
      timeHeader.textContent = time
      content.appendChild(timeHeader)
    }

    if (title) {
      const titleText = document.createElement('p')
      titleText.innerHTML = `<strong>${title}</strong>`
      content.appendChild(titleText)
    }

    while (this.firstChild) {
      content.appendChild(this.firstChild)
    }

    item.appendChild(content)
    this.appendChild(item)
  }
}

// Register all components if window is defined
if (typeof window !== 'undefined') {
  if (!customElements.get('layui-button')) {
    customElements.define('layui-button', LayuiButton)
  }
  if (!customElements.get('layui-badge')) {
    customElements.define('layui-badge', LayuiBadge)
  }
  if (!customElements.get('layui-card')) {
    customElements.define('layui-card', LayuiCard)
  }
  if (!customElements.get('layui-progress')) {
    customElements.define('layui-progress', LayuiProgress)
  }
  if (!customElements.get('layui-timeline')) {
    customElements.define('layui-timeline', LayuiTimeline)
  }
  if (!customElements.get('layui-timeline-item')) {
    customElements.define('layui-timeline-item', LayuiTimelineItem)
  }
}
export {}
