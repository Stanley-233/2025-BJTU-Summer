import { Configuration, DefaultApi } from '../api/generated';
declare const sessionStorage: any;

// 查询日志记录
export async function queryLogs(logType?: string | null, logRange?: string | null, limit?: number, offset?: number, level?: number, onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }));
  try {
    const response = await api.queryLogsLogsGet(logType, logRange, limit, offset, level);
    return response.data;
  } catch (err: any) {
    onError?.('获取日志失败');
    return null;
  }
}

// 查询日志详情
export async function queryLogDetail(logId: string, onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }));
  try {
    const response = await api.queryLogDetailLogDetailGet(logId);
    return response.data;
  } catch (err: any) {
    onError?.('获取日志详情失败');
    return null;
  }
}

// 测试添加日志（仅供测试）
export async function testAddLogs(onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }));
  try {
    const response = await api.testAddLogsLogsTestGet();
    return response.data;
  } catch (err: any) {
    onError?.('添加日志失败');
    return null;
  }
}

export async function queryLogCount(logType?: string | null, logRange?: string | null, level?: number, onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }));
  try {
    const response = await api.getLogCountLogCountsGet(logType, logRange, null, level);
    return response.data;
  } catch (err: any) {
    onError?.('获取日志数量失败');
    return null;
  }
}