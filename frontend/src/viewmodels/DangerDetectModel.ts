import { Configuration, DefaultApi } from '../api/generated'
import type { VideoDetectRequest, VideoDetectResponse } from '../api/generated'
declare const sessionStorage: any

/**
 * 视频流道路病害检测
 * @param video 视频文件的Base64字符串
 * @param modelType 可选，模型类型
 * @param onError 错误回调
 * @returns Promise<VideoDetectResponse | null>
 */
export async function requestVideoDangerDetect(
    video: string,
    modelType?: string,
    onError?: (msg: string) => void
): Promise<VideoDetectResponse | null> {
    const api = new DefaultApi(new Configuration({
        basePath: 'http://127.0.0.1:8000',
        accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
    }))
    try {
        const req: VideoDetectRequest = { video: video, model_type: modelType }
        const response = await api.videoDetectVideoDetectPost(req)
        if (!response || !response.data) {
            onError?.('检测失败，未返回结果')
            return null
        }
        return response.data
    } catch (err: any) {
        if (err.response?.status === 422) {
            onError?.('参数错误')
        } else if (err.response?.status === 404) {
            onError?.('未找到相关信息')
        } else {
            onError?.('未知错误')
        }
        return null
    }
}

