import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout, Button, Tooltip } from 'antd'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SunOutlined,
  MoonOutlined,
} from '@ant-design/icons'
import Sidebar from './components/Sidebar'
import ArticlesPage from './pages/ArticlesPage'
import BriefingPage from './pages/BriefingPage'
import StatsPage from './pages/StatsPage'
import SourcesPage from './pages/SourcesPage'
import ChatPage from './pages/ChatPage'
import TrendsPage from './pages/TrendsPage'
import { useTheme } from './contexts/ThemeContext'

const { Header, Content } = Layout

function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const { theme, toggle } = useTheme()
  const dark = theme === 'dark'

  return (
    <Layout style={{ minHeight: '100vh', background: dark ? '#0f1419' : '#f5f7fa' }}>
      <Sidebar collapsed={collapsed} />
      <Layout
        style={{
          marginLeft: collapsed ? 80 : 220,
          transition: 'margin-left 0.2s',
          background: 'transparent',
        }}
      >
        <Header
          style={{
            padding: '0 24px',
            background: dark ? '#1a1f2e' : '#fff',
            borderBottom: `1px solid ${dark ? '#2a3142' : '#eaecef'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: 18 }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ color: dark ? '#94a3b8' : '#6b7280', fontSize: 13, letterSpacing: 0.3 }}>
              Asayomi · 日本ニュースまとめ
            </div>
            <Tooltip title={dark ? 'Light mode' : 'Dark mode'}>
              <Button
                type="text"
                icon={dark ? <SunOutlined /> : <MoonOutlined />}
                onClick={toggle}
              />
            </Tooltip>
          </div>
        </Header>
        <Content style={{ padding: '24px 32px', maxWidth: 1280, margin: '0 auto', width: '100%' }}>
          <Routes>
            {/* カテゴリは記事ページ内のフィルタタグで切替えるため、
                /category/:category の独立ルートは廃止した。 */}
            <Route path="/" element={<ArticlesPage />} />
            <Route path="/briefing" element={<BriefingPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/trends" element={<TrendsPage />} />
            <Route path="/stats" element={<StatsPage />} />
            <Route path="/sources" element={<SourcesPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  )
}
