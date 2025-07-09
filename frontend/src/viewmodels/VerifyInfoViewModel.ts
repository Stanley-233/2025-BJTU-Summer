import { ref } from 'vue'
import { DefaultApi } from '../api/generated'

export default function useVerifyInfoViewModel(onError?: (msg: string) => void) {
  const api = new DefaultApi()
  const isVerifying = ref(false)

  const sendVerifyEmail = async (email: string) => {
    if (!email) {
      onError?.('邮箱不能为空')
      return
    }
    isVerifying.value = true
    try {
      await api.requestEmailVerificationVerifyEmailPut()
      onError?.('验证邮件已发送，请查收邮箱')
    } catch (e) {
      onError?.('发送验证邮件失败')
    } finally {
      isVerifying.value = false
    }
  }

  return {
    isVerifying,
    sendVerifyEmail
  }
}
