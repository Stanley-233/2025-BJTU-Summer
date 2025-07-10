import { ref } from 'vue'
import {Configuration, DefaultApi} from '../api/generated'

export default async function verifyEmail(onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: localStorage.getItem('token') ? () => localStorage.getItem('token')! : undefined,
  }))
  const isVerifying = ref(false)
  try {
    await api.requestEmailVerificationVerifyEmailPut();
    onError?.('验证邮件已发送，请查收邮箱')
  } catch (err: any) {
    if (err.response?.status === 403) {
      onError?.('认证错误')
    } else if (err.response?.status === 404) {
      onError?.('用户不存在')
    }
  } finally {
    isVerifying.value = false
  }
  return isVerifying
}
