import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout, Button } from 'antd'
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons'
import Sidebar from './components/Sidebar'
import ArticlesPage from './pages/ArticlesPage'
import BriefingPage from './pages/BriefingPage'
import StatsPage from './pages/StatsPage'

const { Header, Content } = Layout

function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar collapsed={collapsed} />
      <Layout style={{ marginLeft: collapsed ? 80 : 220, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            borderBottom: '1px solid #eaecef',
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
          <div style={{ color: '#6b7280', fontSize: 13, letterSpacing: 0.3 }}>
            Asayomi · Japan News Briefing
          </div>
        </Header>
        <Content style={{ padding: '24px 32px', maxWidth: 1280, margin: '0 auto', width: '100%' }}>
          <Routes>
            <Route path="/" element={<ArticlesPage />} />
            <Route path="/briefing" element={<BriefingPage />} />
            <Route path="/stats" element={<StatsPage />} />
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
