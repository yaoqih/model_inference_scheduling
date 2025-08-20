import React from 'react';
import { Layout, Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  NodeIndexOutlined,
  DeploymentUnitOutlined,
  ScheduleOutlined
} from '@ant-design/icons';

const { Header, Content, Footer } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/environments',
      icon: <DatabaseOutlined />,
      label: <Link to="/environments">环境管理</Link>,
    },
    {
      key: '/models',
      icon: <CloudServerOutlined />,
      label: <Link to="/models">模型管理</Link>,
    },
    {
      key: '/nodes',
      icon: <NodeIndexOutlined />,
      label: <Link to="/nodes">节点管理</Link>,
    },
    {
      key: '/deployments',
      icon: <DeploymentUnitOutlined />,
      label: <Link to="/deployments">部署管理</Link>,
    },
    {
      key: '/scheduling',
      icon: <ScheduleOutlined />,
      label: <Link to="/scheduling">调度管理</Link>,
    },
  ];

  return (
    <Layout>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: '18px', fontWeight: 'bold', marginRight: '40px' }}>
          模型推理调度管理平台
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content style={{ padding: '0 50px', marginTop: '16px' }}>
        <div style={{ 
          padding: 24, 
          minHeight: 'calc(100vh - 134px)', 
          background: '#fff',
          borderRadius: '8px'
        }}>
          {children}
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        模型推理调度管理平台 ©2025
      </Footer>
    </Layout>
  );
};

export default MainLayout;