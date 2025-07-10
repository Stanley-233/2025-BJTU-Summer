import { ref } from 'vue'
import { useRouter } from 'vue-router'
// 声明浏览器全局函数
declare function alert(message?: string): void
declare const localStorage: any
// 引入生成的 API
import { DefaultApi, Configuration, UserLoginRequest } from '../api/generated'

const api = new DefaultApi(new Configuration({ basePath: 'http://127.0.0.1:8000' }))

export default function useLoginPageViewModel(onError?: (msg: string) => void) {
  const router = useRouter()
  const username = ref<string>('')
  const password = ref<string>('')
  const onLogin = async () => {
    const requestBody: UserLoginRequest = { username: username.value, password: password.value }
    try {
      const response = await api.loginLoginPost(requestBody)
      const token = response.data?.token
      if (token) {
        localStorage.setItem('token', token)
        router.push('/')
      } else {
        onError?.('登录失败：未获取到令牌')
      }
    } catch (err: any) {
      // 处理不同的错误码，给出更友好的提示
      if (err.response?.status === 404) {
        onError?.('用户不存在，请检查用户名是否正确。')
      } else if (err.response?.status === 403) {
        onError?.('密码错误，请重新输入。')
      } else {
        const msg = err.response?.data?.message || err.message
        onError?.('登录失败：' + msg)
      }
    }
  }
  return { username, password, onLogin }
}
