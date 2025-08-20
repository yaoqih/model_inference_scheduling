import React from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import {
  DatabaseOutlined,
  CloudServerOutlined,
  NodeIndexOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';

const Home: React.FC = () => {
  return (
    <div>
      <h1 style={{ marginBottom: '24px' }}>模型推理调度管理平台</h1>
      
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="环境总数"
              value={0}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="模型总数"
              value={0}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="节点总数"
              value={0}
              prefix={<NodeIndexOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="在线节点"
              value={0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="系统概览" style={{ marginBottom: '24px' }}>
        <p>欢迎使用模型推理调度管理平台！</p>
        <p>本平台提供以下功能：</p>
        <ul>
          <li>环境管理：创建和管理不同的推理环境</li>
          <li>模型管理：部署和配置推理模型，包含RabbitMQ队列配置</li>
          <li>节点管理：监控和管理推理节点状态</li>
          <li>实时监控：查看系统运行状态和性能指标</li>
        </ul>
      </Card>
    </div>
  );
};

export default Home;