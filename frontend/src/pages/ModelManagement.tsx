import React, { useState, useEffect } from 'react';
import { Model, Environment } from '../types';
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
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CloudServerOutlined,
} from '@ant-design/icons';
import { modelAPI, environmentAPI } from '../services/api';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const ModelManagement: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingModel, setEditingModel] = useState<Model | null>(null);
  const [form] = Form.useForm();

  // 获取环境名称的辅助函数
  const getEnvironmentName = (environmentId: number): string => {
    const environment = environments.find(env => env.id === environmentId);
    return environment ? environment.name : '未知环境';
  };

  // 获取模型列表
  const fetchModels = async () => {
    setLoading(true);
    try {
      const response: any = await modelAPI.getAll();
      if (response.data && response.data.success) {
        setModels(response.data.data || []);
      } else {
        setModels(response.data || []);
      }
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

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
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
      title: '操作',
      key: 'actions',
      width: 150,
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
              {environments.map((env: any) => (
                <Option key={env.id} value={env.id}>
                  {env.name}
                </Option>
              ))}
            </Select>
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

export default ModelManagement;