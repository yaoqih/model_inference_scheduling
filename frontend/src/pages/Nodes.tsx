import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Space,
  Popconfirm,
  Typography,
  Tag,
  Badge
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  NodeIndexOutlined,
  ReloadOutlined,
  SearchOutlined
} from '@ant-design/icons';
import { nodeAPI, environmentAPI } from '../services/api';
import { Node, Environment } from '../types';

const { Title } = Typography;
const { Option } = Select;

const Nodes: React.FC = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingNode, setEditingNode] = useState<Node | null>(null);
  const [form] = Form.useForm();

  // 获取节点列表
  const fetchNodes = async () => {
    setLoading(true);
    try {
      const response: any = await nodeAPI.getAll();
      if (response.data && response.data.success) {
        setNodes(response.data.data || []);
      } else {
        setNodes(response.data || []);
      }
    } catch (error) {
      message.error('获取节点列表失败');
      console.error('Error fetching nodes:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取环境列表
  const fetchEnvironments = async () => {
    try {
      const response: any = await environmentAPI.getAll();
      if (response.data && response.data.success) {
        setEnvironments(response.data.data || []);
      } else {
        setEnvironments(response.data || []);
      }
    } catch (error) {
      console.error('Error fetching environments:', error);
    }
  };

  // 组件挂载时获取数据
  useEffect(() => {
    fetchNodes();
    fetchEnvironments();
  }, []);

  // 打开创建/编辑模态框
  const openModal = (node?: Node) => {
    setEditingNode(node || null);
    setModalVisible(true);
    if (node) {
      // 转换后端字段到前端表单字段
      form.setFieldsValue({
        host: node.node_ip,
        port: node.node_port,
        environment_id: node.environment_id,
        available_gpu_ids: node.available_gpu_ids || [],
        available_models: node.available_models || []
      });
    } else {
      form.resetFields();
      // 设置默认端口
      form.setFieldsValue({
        port: 8080
      });
    }
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingNode(null);
    form.resetFields();
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    try {
      // 转换字段名以匹配后端API
      const nodeData = {
        environment_id: values.environment_id,
        node_ip: values.host,
        node_port: values.port,
        available_gpu_ids: values.available_gpu_ids || [],
        available_models: [] // 模型信息将通过动态发现获取
      };

      if (editingNode) {
        // 更新节点
        await nodeAPI.update(editingNode.id!, nodeData);
        message.success('节点更新成功');
      } else {
        // 创建节点
        await nodeAPI.create(nodeData);
        message.success('节点创建成功');
      }
      closeModal();
      fetchNodes();
    } catch (error) {
      message.error(editingNode ? '节点更新失败' : '节点创建失败');
      console.error('Error saving node:', error);
    }
  };

  // 删除节点
  const handleDelete = async (id: number) => {
    try {
      await nodeAPI.delete(id);
      message.success('节点删除成功');
      fetchNodes();
    } catch (error) {
      message.error('节点删除失败');
      console.error('Error deleting node:', error);
    }
  };

  // 检查节点状态
  const checkNodeStatus = async (id: number) => {
    try {
      await nodeAPI.getStatus(id);
      message.success('节点状态检查完成');
      fetchNodes(); // 刷新列表
    } catch (error) {
      message.error('节点状态检查失败');
      console.error('Error checking node status:', error);
    }
  };

  // 发现节点模型
  const discoverNodeModels = async (id: number) => {
    try {
      const response: any = await nodeAPI.discoverModels(id);
      if (response.data && response.data.success) {
        const discoveredCount = response.data.data.discovered_models?.length || 0;
        message.success(`成功发现 ${discoveredCount} 个模型`);
        fetchNodes(); // 刷新列表以显示更新的模型信息
      } else {
        message.warning('模型发现完成，但可能无法连接到节点');
      }
    } catch (error) {
      message.error('模型发现失败');
      console.error('Error discovering models:', error);
    }
  };

  // 获取环境名称
  const getEnvironmentName = (environmentId: number) => {
    const env = environments.find((e: any) => e.id === environmentId);
    return env ? env.name : '未知环境';
  };

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

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      // width: 80,
    },
    {
      title: '节点名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <NodeIndexOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: '主机地址',
      dataIndex: 'node_ip',
      key: 'node_ip',
    },
    {
      title: '端口',
      dataIndex: 'node_port',
      key: 'node_port',
      // width: 100,
    },
    {
      title: '所属环境',
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
      // width: 100,
      render: (status: string) => getStatusBadge(status),
    },
    {
      title: '可用模型',
      dataIndex: 'available_models',
      key: 'available_models',
      // width: 200,
      render: (models: string[]) => {
        if (!models || models.length === 0) {
          return <Tag color="orange">未发现</Tag>;
        }
        return (
          <div>
            {models.map((model, index) => (
              <Tag key={index} color="green" style={{ marginBottom: 4 }}>
                {model}
              </Tag>
            ))}
          </div>
        );
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      // width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      // width: 200,
      render: (_: any, record: Node) => (
        <Space>
          <Button
            type="link"
            icon={<ReloadOutlined />}
            onClick={() => checkNodeStatus(record.id!)}
            title="检查状态"
          >
            检查
          </Button>
          <Button
            type="link"
            icon={<SearchOutlined />}
            onClick={() => discoverNodeModels(record.id!)}
            title="发现可用模型"
          >
            发现模型
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => openModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个节点吗？"
            onConfirm={() => handleDelete(record.id!)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>节点管理</Title>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchNodes}
          >
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openModal()}
          >
            添加节点
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={nodes}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title={editingNode ? '编辑节点' : '添加节点'}
        open={modalVisible}
        onCancel={closeModal}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="节点名称"
            rules={[
              { required: true, message: '请输入节点名称' },
              { max: 100, message: '节点名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="请输入节点名称" />
          </Form.Item>

          <Form.Item
            name="host"
            label="主机地址"
            rules={[
              { required: true, message: '请输入主机地址' },
              { max: 255, message: '主机地址不能超过255个字符' }
            ]}
          >
            <Input placeholder="请输入主机地址，如：192.168.1.100" />
          </Form.Item>

          <Form.Item
            name="port"
            label="端口"
            rules={[
              { required: true, message: '请输入端口号' },
              { type: 'number', min: 1, max: 65535, message: '端口范围1-65535' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="8080"
              min={1}
              max={65535}
            />
          </Form.Item>

          <Form.Item
            name="environment_id"
            label="所属环境"
            rules={[
              { required: true, message: '请选择所属环境' }
            ]}
          >
            <Select placeholder="请选择环境">
              {environments.map((env: any) => (
                <Option key={env.id} value={env.id}>
                  {env.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="available_gpu_ids"
            label="可用GPU ID"
            tooltip="输入可用的GPU ID，多个ID用逗号分隔，如：0,1,2"
          >
            <Select
              mode="tags"
              style={{ width: '100%' }}
              placeholder="请输入GPU ID，如：0,1,2"
              tokenSeparators={[',']}
            />
          </Form.Item>

          <div style={{
            padding: '12px',
            backgroundColor: '#f6ffed',
            border: '1px solid #b7eb8f',
            borderRadius: '6px',
            marginBottom: '16px'
          }}>
            <p style={{ margin: 0, color: '#52c41a', fontSize: '14px' }}>
              💡 <strong>智能发现：</strong>可用模型将在节点注册后自动从节点端获取，无需手动填写
            </p>
          </div>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingNode ? '更新' : '添加'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Nodes;