import '@fontsource-variable/source-sans-3'
import '@fontsource/source-code-pro/400.css'
import './styles/tokens.css'
import './styles/base.css'
import './styles/controls.css'
import './styles/shell.css'
import './styles/feedback.css'
import './styles/footnotes.css'
import './styles/chat.css'
import './styles/layout.css'
import './styles/messages.css'
import './styles/composer.css'
import './styles/forms.css'
import './styles/inspector.css'
import './styles/turns.css'
import './styles/tools.css'
import './styles/sources.css'
import './styles/results.css'
import './styles/tables.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'

const root = document.getElementById('root')
if (!root) throw new Error('Missing #root element in index.html')

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
