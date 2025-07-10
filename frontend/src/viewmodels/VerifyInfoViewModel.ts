import { ref } from 'vue'
import {Configuration, DefaultApi} from '../api/generated'
declare const sessionStorage:any

export async function verifyEmail(onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
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

export async function codeCheck(code: string, onError?: (msg: string) => void) {
  const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
  }))
  try {
    const response = await api.verifyEmailCodeVerifyEmailCodePost(code)
    if (response?.status === 201) {
      onError?.('未请求验证码')
      return 0;
    } else if (response?.status === 202) {
      onError?.('验证码已过期')
      return 1;
    } else if (response?.status === 203) {
      onError?.('验证码错误')
      return 2;
    } else if (response?.status != 200) {
      onError?.('Super Big Mistake!!!')
      return 2;
    }
    return true;
  } catch (err: any) {
    if (err.response?.status === 401) {
      onError?.('认证错误')
    } else if (err.response?.status === 404) {
      onError?.('用户不存在')
    } else if (err.response?.status === 422) {
      onError?.('Validation error')
    }
    return 1;
  }
}