import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider, theme as antdTheme } from 'antd'
import jaJP from 'antd/locale/ja_JP'
import App from './App'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'
import './styles/index.css'

function ThemedApp() {
  const { theme } = useTheme()
  return (
    <ConfigProvider
      locale={jaJP}
      theme={{
        algorithm: theme === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        token: {
          colorPrimary: '#667eea',
          borderRadius: 8,
        },
      }}
    >
      <App />
    </ConfigProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <ThemedApp />
    </ThemeProvider>
  </React.StrictMode>
)
