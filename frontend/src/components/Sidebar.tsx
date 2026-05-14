import { Layout, Menu, Typography } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ReadOutlined,
  FileTextOutlined,
  BarChartOutlined,
  DatabaseOutlined,
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
    { key: '/', icon: <ReadOutlined />, label: 'Articles' },
    { key: '/briefing', icon: <FileTextOutlined />, label: 'Briefing' },
    { key: '/stats', icon: <BarChartOutlined />, label: 'Stats' },
    { key: '/sources', icon: <DatabaseOutlined />, label: 'Sources' },
  ]

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
        selectedKeys={[location.pathname]}
        items={items}
        onClick={({ key }) => navigate(key)}
        style={{ background: 'transparent', borderRight: 0, paddingTop: 8 }}
      />
    </Sider>
  )
}
