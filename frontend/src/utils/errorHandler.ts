import { message } from 'antd';

// 全局错误处理函数
export const handleError = (error: any) => {
  console.error('Error:', error);
  if (error.response) {
    // 服务器返回的错误
    message.error(`错误: ${error.response.data.message || '未知错误'}`);
  } else if (error.request) {
    // 请求未收到响应
    message.error('请求未收到响应，请检查网络连接');
  } else {
    // 其他错误
    message.error(`错误: ${error.message}`);
  }
};