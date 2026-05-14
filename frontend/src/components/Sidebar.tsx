import { Layout, Menu, Typography } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  FileTextOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  MessageOutlined,
  LineChartOutlined,
  AppstoreOutlined,
  CodeOutlined,
  DollarCircleOutlined,
  GlobalOutlined,
} from '@ant-design/icons'

const { Sider } = Layout
const { Text } = Typography

interface SidebarProps {
  collapsed: boolean
}

export default function Sidebar({ collapsed }: SidebarProps) {
  const navigate = useNavigate()
  const location = useLocation()

  const items = [
    { key: '/', icon: <HomeOutlined />, label: 'All Articles' },
    { type: 'divider' as const },
    { key: '/category/総合', icon: <AppstoreOutlined />, label: '総合' },
    { key: '/category/テクノロジー', icon: <CodeOutlined />, label: 'テクノロジー' },
    { key: '/category/経済・ビジネス', icon: <DollarCircleOutlined />, label: '経済・ビジネス' },
    { key: '/category/国際', icon: <GlobalOutlined />, label: '国際' },
    { type: 'divider' as const },
    { key: '/briefing', icon: <FileTextOutlined />, label: 'Briefing' },
    { key: '/chat', icon: <MessageOutlined />, label: 'Chat' },
    { key: '/trends', icon: <LineChartOutlined />, label: 'Trends' },
    { key: '/stats', icon: <BarChartOutlined />, label: 'Stats' },
    { key: '/sources', icon: <DatabaseOutlined />, label: 'Sources' },
  ]

  // 现在的路径如果是 /category/xxx，把 selectedKey 设置为完整路径
  const selectedKey = decodeURIComponent(location.pathname)

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      theme="dark"
      width={220}
      trigger={null}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        background: 'var(--gradient-sidebar)',
        boxShadow: '2px 0 12px rgba(0, 0, 0, 0.15)',
      }}
    >
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          padding: collapsed ? 0 : '0 20px',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          gap: 10,
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: 10,
            background: 'var(--gradient-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: 18,
            color: '#fff',
            letterSpacing: '-0.5px',
            boxShadow: '0 2px 10px rgba(102,126,234,0.4)',
          }}
        >
          A
        </div>
        {!collapsed && (
          <Text className="logo-text" style={{ fontSize: 20 }}>
            Asayomi
          </Text>
        )}
      </div>
      <Menu
        mode="inline"
        theme="dark"
        selectedKeys={[selectedKey]}
        items={items}
        onClick={({ key }) => navigate(key)}
        style={{ background: 'transparent', borderRight: 0, paddingTop: 8 }}
      />
    </Sider>
  )
}
