import React, { useState, useEffect } from 'react';
import { Table, Switch, Button, Modal, Form, Input, message, Popconfirm } from 'antd';
import { schedulingStrategyAPI } from '../services/api';
import { SchedulingStrategy } from '../types';

const Scheduling: React.FC = () => {
  const [strategies, setStrategies] = useState<SchedulingStrategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<SchedulingStrategy | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    setLoading(true);
    try {
      const response = await schedulingStrategyAPI.getAll();
      setStrategies(response.data);
    } catch (error) {
      message.error('加载调度策略失败');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (strategy: SchedulingStrategy) => {
    try {
      await schedulingStrategyAPI.update(strategy.id, { is_active: !strategy.is_active });
      message.success('策略状态更新成功');
      fetchStrategies();
    } catch (error) {
      message.error('更新策略状态失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await schedulingStrategyAPI.delete(id);
      message.success('删除策略成功');
      fetchStrategies();
    } catch (error) {
      message.error('删除策略失败');
    }
  };

  const showModal = (strategy: SchedulingStrategy | null = null) => {
    setEditingStrategy(strategy);
    form.setFieldsValue(strategy || { name: '', description: '' });
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingStrategy(null);
    form.resetFields();
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingStrategy) {
        await schedulingStrategyAPI.update(editingStrategy.id, values);
        message.success('更新策略成功');
      } else {
        await schedulingStrategyAPI.create(values);
        message.success('创建策略成功');
      }
      fetchStrategies();
      handleCancel();
    } catch (error) {
      message.error('保存策略失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    {
      title: '是否激活',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean, record: SchedulingStrategy) => (
        <Switch checked={isActive} onChange={() => handleToggleActive(record)} />
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: SchedulingStrategy) => (
        <span>
          <Button type="link" onClick={() => showModal(record)}>编辑</Button>
          <Popconfirm
            title="确定删除此策略吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="是"
            cancelText="否"
          >
            <Button type="link" danger>删除</Button>
          </Popconfirm>
        </span>
      ),
    },
  ];

  return (
    <div>
      <Button type="primary" onClick={() => showModal()} style={{ marginBottom: 16 }}>
        添加策略
      </Button>
      <Table
        columns={columns}
        dataSource={strategies}
        loading={loading}
        rowKey="id"
      />
      <Modal
        title={editingStrategy ? '编辑策略' : '添加策略'}
        visible={isModalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入策略名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Scheduling;