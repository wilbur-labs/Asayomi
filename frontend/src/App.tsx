import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import { ReadOutlined, FileTextOutlined, BarChartOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import ArticlesPage from './pages/ArticlesPage'
import BriefingPage from './pages/BriefingPage'
import StatsPage from './pages/StatsPage'

const { Header, Content } = Layout

function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/', icon: <ReadOutlined />, label: 'ニュース一覧' },
    { key: '/briefing', icon: <FileTextOutlined />, label: '今日のブリーフィング' },
    { key: '/stats', icon: <BarChartOutlined />, label: '統計' },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <h1 style={{ color: '#fff', margin: '0 24px 0 0', fontSize: 18 }}>朝読み</h1>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1 }}
        />
      </Header>
      <Content style={{ padding: '24px', maxWidth: 1200, margin: '0 auto', width: '100%' }}>
        <Routes>
          <Route path="/" element={<ArticlesPage />} />
          <Route path="/briefing" element={<BriefingPage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </Content>
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
