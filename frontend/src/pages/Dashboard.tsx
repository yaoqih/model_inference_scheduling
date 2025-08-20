import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Badge,
  Progress,
  Typography,
  Space,
  Button,
  Tag
} from 'antd';
import {
  DatabaseOutlined,
  CloudServerOutlined,
  NodeIndexOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { environmentAPI, modelAPI, nodeAPI } from '../services/api';
import { Environment, Model, Node } from '../types';

const { Title } = Typography;

interface DashboardStats {
  totalEnvironments: number;
  totalModels: number;
  totalNodes: number;
  onlineNodes: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalEnvironments: 0,
    totalModels: 0,
    totalNodes: 0,
    onlineNodes: 0
  });
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取统计数据
  const fetchStats = async () => {
    setLoading(true);
    try {
      // 获取环境数据
      const envResponse: any = await environmentAPI.getAll();
      const envData = envResponse.data?.success ? envResponse.data.data : envResponse.data || [];
      setEnvironments(envData);

      // 获取模型数据
      const modelResponse: any = await modelAPI.getAll();
      const modelData = modelResponse.data?.success ? modelResponse.data.data : modelResponse.data || [];
      setModels(modelData);

      // 获取节点数据
      const nodeResponse: any = await nodeAPI.getAll();
      const nodeData = nodeResponse.data?.success ? nodeResponse.data.data : nodeResponse.data || [];
      setNodes(nodeData);

      // 计算统计数据
      const onlineNodes = nodeData.filter((node: Node) => node.status === 'online').length;
      
      setStats({
        totalEnvironments: envData.length,
        totalModels: modelData.length,
        totalNodes: nodeData.length,
        onlineNodes: onlineNodes
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时获取数据
  useEffect(() => {
    fetchStats();
    // 设置定时刷新
    const interval = setInterval(fetchStats, 30000); // 每30秒刷新一次
    return () => clearInterval(interval);
  }, []);

  // 获取状态标签
  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'online':
        return <Badge status="success" text="在线" />;
      case 'offline':
        return <Badge status="error" text="离线" />;
      default:
        return <Badge status="default" text="未知" />;
    }
  };

  // 获取环境名称
  const getEnvironmentName = (environmentId: number) => {
    const env = environments.find((e: any) => e.id === environmentId);
    return env ? env.name : '未知环境';
  };

  // 节点表格列定义
  const nodeColumns = [
    {
      title: '节点名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <NodeIndexOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: '地址',
      key: 'address',
      render: (_: any, record: Node) => `${record.node_ip}:${record.node_port}`,
    },
    {
      title: '环境',
      dataIndex: 'environment_id',
      key: 'environment_id',
      render: (environmentId: number) => (
        <Tag color="blue">{getEnvironmentName(environmentId)}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusBadge(status),
    },
    {
      title: '最后更新',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text: string) => text ? new Date(text).toLocaleString() : '-',
    },
  ];

  // 模型表格列定义
  const modelColumns = [
    {
      title: '模型名称',
      dataIndex: 'model_name',
      key: 'model_name',
      render: (text: string) => (
        <Space>
          <CloudServerOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: '环境',
      dataIndex: 'environment_id',
      key: 'environment_id',
      render: (environmentId: number) => (
        <Tag color="blue">{getEnvironmentName(environmentId)}</Tag>
      ),
    },
    {
      title: 'RabbitMQ主机',
      dataIndex: 'rabbitmq_host',
      key: 'rabbitmq_host',
    },
    {
      title: '队列名称',
      dataIndex: 'queue_name',
      key: 'queue_name',
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>实时监控面板</Title>
        <Button
          icon={<ReloadOutlined />}
          onClick={fetchStats}
          loading={loading}
        >
          刷新数据
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="环境总数"
              value={stats.totalEnvironments}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="模型总数"
              value={stats.totalModels}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="节点总数"
              value={stats.totalNodes}
              prefix={<NodeIndexOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="在线节点"
              value={stats.onlineNodes}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress
              percent={stats.totalNodes > 0 ? Math.round((stats.onlineNodes / stats.totalNodes) * 100) : 0}
              size="small"
              status={stats.onlineNodes === stats.totalNodes ? 'success' : 'active'}
            />
          </Card>
        </Col>
      </Row>

      {/* 节点状态 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="节点状态" extra={<NodeIndexOutlined />}>
            <Table
              columns={nodeColumns}
              dataSource={nodes}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 5 }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="模型状态" extra={<CloudServerOutlined />}>
            <Table
              columns={modelColumns}
              dataSource={models}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 5 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 环境概览 */}
      <Card title="环境概览" extra={<DatabaseOutlined />}>
        <Row gutter={16}>
          {environments.map((env: any) => {
            const envModels = models.filter((model: any) => model.environment_id === env.id);
            const envNodes = nodes.filter((node: any) => node.environment_id === env.id);
            const onlineEnvNodes = envNodes.filter((node: any) => node.status === 'online');
            
            return (
              <Col span={8} key={env.id} style={{ marginBottom: 16 }}>
                <Card size="small" title={env.name}>
                  <div style={{ marginBottom: 8 }}>
                    <Space>
                      <CloudServerOutlined />
                      <span>模型: {envModels.length}</span>
                    </Space>
                  </div>
                  <div style={{ marginBottom: 8 }}>
                    <Space>
                      <NodeIndexOutlined />
                      <span>节点: {envNodes.length}</span>
                    </Space>
                  </div>
                  <div>
                    <Space>
                      <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      <span>在线: {onlineEnvNodes.length}</span>
                    </Space>
                  </div>
                  {envNodes.length > 0 && (
                    <Progress
                      percent={Math.round((onlineEnvNodes.length / envNodes.length) * 100)}
                      size="small"
                      style={{ marginTop: 8 }}
                    />
                  )}
                </Card>
              </Col>
            );
          })}
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard;