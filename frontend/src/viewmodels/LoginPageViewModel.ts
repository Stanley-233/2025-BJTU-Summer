import { ref } from 'vue'
import { useRouter } from 'vue-router'
// 声明浏览器全局函数
declare function alert(message?: string): void
declare const localStorage: any
// 引入生成的 API
import { DefaultApi, Configuration, UserLoginRequest } from '../api/generated'

const api = new DefaultApi(new Configuration({ basePath: 'http://127.0.0.1:8000' }))

export default function useLoginPageViewModel() {
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
        alert('登录失败：未获取到令牌')
      }
    } catch (err: any) {
      alert('登录失败：' + (err.response?.data?.message || err.message))
    }
  }

  return { username, password, onLogin }
}
