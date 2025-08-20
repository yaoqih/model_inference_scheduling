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
  Divider
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CloudServerOutlined,
  SettingOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { modelAPI, environmentAPI, queueAPI } from '../services/api';
import { Model, Environment, QueueLengthRecord } from '../types';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 队列历史图表组件
const QueueHistoryChart: React.FC<{ modelId: number }> = ({ modelId }) => {
  const [history, setHistory] = useState<QueueLengthRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const response: any = await queueAPI.getQueueHistory(modelId, 100);
        if (response.data && response.data.success) {
          // 对数据进行排序和格式化
          const formattedData = response.data.data
            .map((d: QueueLengthRecord) => ({
              ...d,
              timestamp: new Date(d.timestamp).toLocaleString(),
            }))
            .reverse();
          setHistory(formattedData);
        }
      } catch (error) {
        message.error('获取队列历史记录失败');
        console.error(`Error fetching queue history for model ${modelId}:`, error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [modelId]);

  if (loading) {
    return <p>加载历史记录中...</p>;
  }

  if (history.length === 0) {
    return <p>暂无历史记录</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={history}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" angle={-30} textAnchor="end" height={70} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="length" name="队列长度" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
};


const Models: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingModel, setEditingModel] = useState<Model | null>(null);
  const [form] = Form.useForm();

  // 获取模型列表并附带队列信息
  const fetchModels = async () => {
    setLoading(true);
    try {
      const response: any = await modelAPI.getAll();
      let fetchedModels: Model[] = [];
      if (response.data && response.data.success) {
        fetchedModels = response.data.data || [];
      } else {
        fetchedModels = response.data || [];
      }

      // 为每个模型异步获取队列信息
      const modelsWithQueueInfo = await Promise.all(
        fetchedModels.map(async (model) => {
          if (model.id && model.rabbitmq_queue_name) {
            try {
              const queueResponse: any = await queueAPI.getQueueInfo(model.id);
              if (queueResponse.data && queueResponse.data.success) {
                return {
                  ...model,
                  queue_length: queueResponse.data.data.messages,
                };
              }
            } catch (queueError) {
              console.error(`Failed to fetch queue info for model ${model.id}:`, queueError);
            }
          }
          return { ...model, queue_length: undefined }; // 如果没有队列名或获取失败
        })
      );
      
      setModels(modelsWithQueueInfo);

    } catch (error) {
      message.error('获取模型列表失败');
      console.error('Error fetching models:', error);
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
    fetchModels();
    fetchEnvironments();
  }, []);

  // 打开创建/编辑模态框
  const openModal = (model?: Model) => {
    setEditingModel(model || null);
    setModalVisible(true);
    if (model) {
      form.setFieldsValue(model);
    } else {
      form.resetFields();
      // 设置默认值
      form.setFieldsValue({
        rabbitmq_host: 'localhost',
        rabbitmq_port: 15672,
        rabbitmq_username: 'guest',
        rabbitmq_password: 'guest'
      });
    }
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingModel(null);
    form.resetFields();
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    try {
      if (editingModel) {
        // 更新模型
        await modelAPI.update(editingModel.id!, values);
        message.success('模型更新成功');
      } else {
        // 创建模型
        await modelAPI.create(values);
        message.success('模型创建成功');
      }
      closeModal();
      fetchModels();
    } catch (error) {
      message.error(editingModel ? '模型更新失败' : '模型创建失败');
      console.error('Error saving model:', error);
    }
  };

  // 删除模型
  const handleDelete = async (id: number) => {
    try {
      await modelAPI.delete(id);
      message.success('模型删除成功');
      fetchModels();
    } catch (error) {
      message.error('模型删除失败');
      console.error('Error deleting model:', error);
    }
  };

  // 获取环境名称
  const getEnvironmentName = (environmentId: number) => {
    const env = environments.find(e => e.id === environmentId);
    return env ? env.name : '未知环境';
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
      title: '模型名称',
      dataIndex: 'model_name',
      key: 'model_name',
      render: (text: string) => (
        <Space>
          <CloudServerOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
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
      title: '平均推理时间(s)',
      dataIndex: 'average_inference_time',
      key: 'average_inference_time',
      render: (time: number) => time ? `${time.toFixed(2)}s` : '-',
    },
    {
      title: 'RabbitMQ配置',
      key: 'rabbitmq',
      // width: 200,
      render: (_: any, record: Model) => (
        <div>
          <div>主机: {record.rabbitmq_host}:{record.rabbitmq_port}</div>
          <div>队列: {record.rabbitmq_queue_name}</div>
          <div>
            长度: {typeof record.queue_length === 'number'
              ? <Tag color={record.queue_length > 0 ? "orange" : "green"}>{record.queue_length}</Tag>
              : <Tag>未知</Tag>}
          </div>
        </div>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      // width: 150,
      render: (_: any, record: Model) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => openModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个模型吗？"
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
        <Title level={2}>模型管理</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => openModal()}
        >
          创建模型
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={models}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number) => `共 ${total} 条记录`,
          }}
          expandable={{
            expandedRowRender: record => <QueueHistoryChart modelId={record.id!} />,
            rowExpandable: record => !!record.rabbitmq_queue_name,
            expandIcon: ({ expanded, onExpand, record }) =>
              record.rabbitmq_queue_name ? (
                <Button
                  type="link"
                  onClick={e => onExpand(record, e)}
                  icon={<LineChartOutlined />}
                  disabled={!record.rabbitmq_queue_name}
                >
                  {expanded ? '收起图表' : '查看历史'}
                </Button>
              ) : null,
          }}
        />
      </Card>

      <Modal
        title={editingModel ? '编辑模型' : '创建模型'}
        open={modalVisible}
        onCancel={closeModal}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="model_name"
            label="模型名称"
            rules={[
              { required: true, message: '请输入模型名称' },
              { max: 100, message: '模型名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="请输入模型名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
            rules={[
              { max: 500, message: '描述不能超过500个字符' }
            ]}
          >
            <TextArea
              rows={3}
              placeholder="请输入模型描述（可选）"
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
              {environments.map(env => (
                <Option key={env.id} value={env.id}>
                  {env.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="average_inference_time"
            label="平均推理时间(秒)"
            rules={[
              { type: 'number', min: 0, message: '请输入有效的秒数' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入模型平均推理时间（秒）"
              min={0}
              step={0.01}
            />
          </Form.Item>

          <Divider orientation="left">
            <Space>
              <SettingOutlined />
              RabbitMQ配置
            </Space>
          </Divider>

          <Form.Item
            name="rabbitmq_host"
            label="RabbitMQ主机"
            rules={[
              { required: true, message: '请输入RabbitMQ主机地址' }
            ]}
          >
            <Input placeholder="localhost" />
          </Form.Item>

          <Form.Item
            name="rabbitmq_port"
            label="RabbitMQ端口"
            rules={[
              { required: true, message: '请输入RabbitMQ端口' },
              { type: 'number', min: 1, max: 65535, message: '端口范围1-65535' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="5672"
              min={1}
              max={65535}
            />
          </Form.Item>

          <Form.Item
            name="rabbitmq_username"
            label="RabbitMQ用户名"
            rules={[
              { required: true, message: '请输入RabbitMQ用户名' }
            ]}
          >
            <Input placeholder="guest" />
          </Form.Item>

          <Form.Item
            name="rabbitmq_password"
            label="RabbitMQ密码"
            rules={[
              { required: true, message: '请输入RabbitMQ密码' }
            ]}
          >
            <Input.Password placeholder="guest" />
          </Form.Item>

          <Form.Item
            name="rabbitmq_queue_name"
            label="队列名称"
            rules={[
              { required: true, message: '请输入队列名称' },
              { max: 100, message: '队列名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="请输入队列名称" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingModel ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Models;