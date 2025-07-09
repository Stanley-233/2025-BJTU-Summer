import { ref } from 'vue'
import { useRouter } from 'vue-router'
// 声明浏览器全局函数
declare function alert(message?: string): void
// 引入生成的 API
import { DefaultApi, Configuration, UserRegisterRequest } from '../api/generated'

const api = new DefaultApi(new Configuration({ basePath: 'http://127.0.0.1:8000' }))

export default function useRegisterPageViewModel(onError?: (msg: string) => void, onSuccess?: (msg: string) => void) {
  const router = useRouter()
  const username = ref<string>('')
  const email = ref<string>('')
  const password = ref<string>('')
  const confirm = ref<string>('')

  const onRegister = async () => {
    // 只做非空校验，邮箱格式交由浏览器原生input type=email处理
    if (!email.value) {
      onError?.('请输入邮箱地址')
      return
    }
    if (password.value !== confirm.value) {
      onError?.('两次输入的密码不一致')
      return
    }
    const requestBody: UserRegisterRequest = { username: username.value, email: email.value, phone: null, password: password.value }
    try {
      await api.registerRegisterPost(requestBody)
      onSuccess?.('注册成功，欢迎加入！')
      await router.push('/login')
    } catch (err: any) {
      if (err.response?.status === 400) {
        onError?.('用户名或邮箱已被注册，请更换后重试。')
      } else {
        onError?.('注册失败：' + (err.response?.data?.message || err.message))
      }
    }
  }

  return { username, email, password, confirm, onRegister }
}
