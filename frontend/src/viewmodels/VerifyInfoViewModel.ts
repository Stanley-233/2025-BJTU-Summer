import { ref } from 'vue'
import {Configuration, DefaultApi} from '../api/generated'
declare const sessionStorage:any

export async function verifyEmail(onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => localStorage.getItem('token')! : undefined,
  }))
  try {
    await api.requestEmailVerificationVerifyEmailPut()
    onError?.('验证邮件已发送，请查收邮箱')
  } catch (err: any) {
    if (err.response?.status === 403) {
      onError?.('认证错误')
    } else if (err.response?.status === 404) {
      onError?.('用户不存在')
    }
  }
}

export async function getUserEmail() {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }))
  let response
  try {
    response = await api.getUserEmailGetUserEmailGet()
    return response.data
  } catch (err: any) {
    return null
  }
}

export async function getUserInfo() {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }))
  let response
  try {
    response = await api.getUserInfoGetUserInfoGet()
    return response.data
  } catch (err: any) {
    return null
  }
}