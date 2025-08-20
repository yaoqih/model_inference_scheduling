import React, { useState, useEffect } from 'react';
import { Card, Col, Row, Select, Button, message, Spin, Typography, Tag, Progress, Statistic } from 'antd';
import { deploymentAPI, nodeAPI } from '../services/api';
import { NodeDeploymentStatus, GPUDeploymentStatus, DeploymentSummary, ModelDeploymentStat } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;

const REFRESH_INTERVAL = 10000; // 10秒

const Deployments: React.FC = () => {
    const [summary, setSummary] = useState<DeploymentSummary | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [switching, setSwitching] = useState<{[key: string]: boolean}>({});

    const fetchDeployments = async () => {
        if (document.hidden) return; // 如果页面不可见，则不刷新
        setLoading(true);
        try {
            // 1. 获取基础的部署状态
            const summaryRes = await deploymentAPI.getStatus();
            const initialSummary = summaryRes.data.data as DeploymentSummary;

            if (!initialSummary || !initialSummary.deployment_statuses) {
                setSummary(initialSummary);
                return;
            }

            // 2. 并行获取所有节点支持的模型列表
            const supportedModelsPromises = initialSummary.deployment_statuses.map(node =>
                nodeAPI.discoverSupportedModels(node.node_id).catch(err => {
                    console.error(`获取节点 ${node.node_id} 支持的模型失败:`, err);
                    return null; // 发生错误时返回null，避免Promise.all中断
                })
            );
            const supportedModelsResults = await Promise.all(supportedModelsPromises);

            // 3. 将实时获取的模型列表合并到状态中
            const updatedDeploymentStatuses = initialSummary.deployment_statuses.map((node, index) => {
                const result = supportedModelsResults[index];
                if (result && result.data && result.data.data) {
                    const supportedModels = result.data.data; // API返回的数据结构是 { "MAM": "triton", ... }
                    const modelNames = Object.keys(supportedModels);
                    
                    // 合并并去重模型列表
                    const updatedModels = Array.from(new Set([...node.available_models, ...modelNames]));
                    return { ...node, available_models: updatedModels };
                }
                return node; // 如果获取失败，则返回原始节点数据
            });

            // 4. 设置最终的、合并后的状态
            setSummary({ ...initialSummary, deployment_statuses: updatedDeploymentStatuses });

        } catch (error) {
            message.error('获取部署状态失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDeployments();
        const intervalId = setInterval(fetchDeployments, REFRESH_INTERVAL);
        return () => clearInterval(intervalId);
    }, []);

    const handleModelChange = async (nodeId: number, gpuId: number, newModelName: string, oldModelName?: string) => {
        const switchKey = `${nodeId}-${gpuId}`;
        setSwitching(prev => ({ ...prev, [switchKey]: true }));

        try {
            if (oldModelName) {
                await nodeAPI.stopModel(nodeId, oldModelName, gpuId);
                message.success(`模型 ${oldModelName} 停止指令已发送`);
            }
            if (newModelName) {
                await nodeAPI.startModel(nodeId, newModelName, gpuId);
                message.success(`模型 ${newModelName} 启动指令已发送`);
            }
            setTimeout(fetchDeployments, 1000); // 延迟1秒刷新，等待指令生效
        } catch (error) {
            message.error('模型切换失败，请检查节点连接或后台日志。');
            fetchDeployments();
        } finally {
            setSwitching(prev => ({ ...prev, [switchKey]: false }));
        }
    };

    const renderGpuCard = (node: NodeDeploymentStatus, gpu: GPUDeploymentStatus) => {
        const switchKey = `${node.node_id}-${gpu.gpu_id}`;
        const isSwitching = switching[switchKey] === true;
        const isAvailable = node.available_gpu_ids.includes(gpu.gpu_id);

        // 后端返回的 gpu_load 就是显存使用率百分比
        const memoryUsagePercent = gpu.gpu_load || 0;
        const powerDrawPercent = (gpu.power_usage && gpu.power_limit) ? (gpu.power_usage / gpu.power_limit) * 100 : 0;

        const cardTitle = (
            <span>
                GPU {gpu.gpu_id} {isAvailable && <Tag color="blue">可用</Tag>}
            </span>
        );

        return (
            <Card
                key={gpu.gpu_id}
                title={cardTitle}
                style={{ marginBottom: 16 }}
                extra={
                    isAvailable && (
                        <Select
                            style={{ width: 200 }}
                            placeholder="选择模型进行切换"
                            onChange={(newModel) => handleModelChange(node.node_id, gpu.gpu_id, newModel, gpu.deployed_model?.model_name)}
                            value={gpu.deployed_model?.model_name}
                            disabled={isSwitching}
                        >
                            {node.available_models.map(model => (
                                <Option key={model} value={model}>{model}</Option>
                            ))}
                            <Option key="stop" value=""><em>停止模型</em></Option>
                        </Select>
                    )
                }
            >
                <Spin spinning={isSwitching} tip="切换中...">
                    {gpu.deployed_model ? (
                        <div>
                            <p><strong>模型:</strong> {gpu.deployed_model.model_name}</p>
                            <p><strong>状态:</strong> <Tag color="green">运行中</Tag></p>
                        </div>
                    ) : (
                        <p>无模型运行</p>
                    )}
                    <Row gutter={[16, 0]}>
                        {gpu.gpu_load !== undefined && gpu.gpu_load !== null && (
                            <Col xs={24} lg={12}>
                                <Text strong>显存:</Text>
                                <Progress percent={parseFloat(memoryUsagePercent.toFixed(1))} format={() => `${(gpu.memory_used || 0).toFixed(0)}MB / ${(gpu.memory_total || 0).toFixed(0)}MB`} />
                            </Col>
                        )}

                        {gpu.power_usage !== undefined && gpu.power_limit !== undefined && (
                             <Col xs={24} lg={12}>
                                <Text strong>功耗:</Text>
                                <Progress percent={parseFloat(powerDrawPercent.toFixed(1))} format={() => `${(gpu.power_usage || 0).toFixed(0)}W / ${(gpu.power_limit || 0).toFixed(0)}W`} />
                            </Col>
                        )}
                    </Row>
                </Spin>
            </Card>
        );
    };
    
    const renderSummary = (stats: ModelDeploymentStat[]) => (
        <Card style={{ marginBottom: 24 }}>
            <Title level={4}>模型部署统计</Title>
            <Row gutter={[16, 16]}>
                {stats.map(stat => (
                    <Col xs={12} sm={8} md={6} lg={4} key={stat.model_name}>
                        <Statistic title={stat.model_name} value={stat.count} suffix="个实例" />
                    </Col>
                ))}
            </Row>
        </Card>
    );

    return (
        <div>
            <Title level={2}>模型部署管理</Title>
            <Button onClick={fetchDeployments} loading={loading} style={{ marginBottom: 16 }}>
                立即刷新
            </Button>
            <Spin spinning={loading && !summary}>
                {summary?.model_stats && summary.model_stats.length > 0 && renderSummary(summary.model_stats)}
                <Row gutter={[16, 16]}>
                    {summary?.deployment_statuses.map(node => (
                        <Col xs={24} md={12} lg={8} key={node.node_id}>
                            <Card title={`节点: ${node.node_ip}:${node.node_port}`} type="inner">
                                {node.gpus.map(gpu => renderGpuCard(node, gpu))}
                            </Card>
                        </Col>
                    ))}
                </Row>
            </Spin>
        </div>
    );
};

export default Deployments;