import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  message,
  Space,
  Popconfirm,
  Typography
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import { environmentAPI } from '../services/api';
import { Environment } from '../types';

const { Title } = Typography;
const { TextArea } = Input;

const Environments: React.FC = () => {
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingEnvironment, setEditingEnvironment] = useState<Environment | null>(null);
  const [form] = Form.useForm();

  // 获取环境列表
  const fetchEnvironments = async () => {
    setLoading(true);
    try {
      const response: any = await environmentAPI.getAll();
      // 处理后端返回的格式：{success: true, data: [...]}
      if (response.data && response.data.success) {
        setEnvironments(response.data.data || []);
      } else {
        setEnvironments(response.data || []);
      }
    } catch (error) {
      message.error('获取环境列表失败');
      console.error('Error fetching environments:', error);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时获取数据
  useEffect(() => {
    fetchEnvironments();
  }, []);

  // 打开创建/编辑模态框
  const openModal = (environment?: Environment) => {
    setEditingEnvironment(environment || null);
    setModalVisible(true);
    if (environment) {
      form.setFieldsValue(environment);
    } else {
      form.resetFields();
    }
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingEnvironment(null);
    form.resetFields();
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    try {
      if (editingEnvironment) {
        // 更新环境
        await environmentAPI.update(editingEnvironment.id!, values);
        message.success('环境更新成功');
      } else {
        // 创建环境
        await environmentAPI.create(values);
        message.success('环境创建成功');
      }
      closeModal();
      fetchEnvironments();
    } catch (error) {
      message.error(editingEnvironment ? '环境更新失败' : '环境创建失败');
      console.error('Error saving environment:', error);
    }
  };

  // 删除环境
  const handleDelete = async (id: number) => {
    try {
      await environmentAPI.delete(id);
      message.success('环境删除成功');
      fetchEnvironments();
    } catch (error) {
      message.error('环境删除失败');
      console.error('Error deleting environment:', error);
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
      title: '环境名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <DatabaseOutlined />
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
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      // width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      // width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      // width: 150,
      render: (_: any, record: Environment) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => openModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个环境吗？"
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
        <Title level={2}>环境管理</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => openModal()}
        >
          创建环境
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={environments}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title={editingEnvironment ? '编辑环境' : '创建环境'}
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
            label="环境名称"
            rules={[
              { required: true, message: '请输入环境名称' },
              { max: 100, message: '环境名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="请输入环境名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
            rules={[
              { max: 500, message: '描述不能超过500个字符' }
            ]}
          >
            <TextArea
              rows={4}
              placeholder="请输入环境描述（可选）"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingEnvironment ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Environments;