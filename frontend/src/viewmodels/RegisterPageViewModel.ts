import { ref } from 'vue'
import { useRouter } from 'vue-router'
// 声明浏览器全局函数
declare function alert(message?: string): void
// 引入生成的 API
import { DefaultApi, Configuration, UserRegisterRequest } from '../api/generated'

const api = new DefaultApi(new Configuration({ basePath: 'http://127.0.0.1:8000' }))

export default function useRegisterPageViewModel() {
  const router = useRouter()
  const username = ref<string>('')
  const email = ref<string>('')
  const password = ref<string>('')
  const confirm = ref<string>('')

  const onRegister = async () => {
    if (password.value !== confirm.value) {
      alert('两次输入的密码不一致')
      return
    }
    const requestBody: UserRegisterRequest = { username: username.value, email: email.value, phone: null, password: password.value }
    try {
      await api.registerRegisterPost(requestBody)
      alert('注册成功')
      await router.push('/login')
    } catch (err: any) {
      alert('注册失败：' + (err.response?.data?.message || err.message))
    }
  }

  return { username, email, password, confirm, onRegister }
}
