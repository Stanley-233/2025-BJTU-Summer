import {Configuration, DefaultApi} from '../api/generated'
declare const sessionStorage:any
const api = new DefaultApi(new Configuration({
    basePath: 'http://127.0.0.1:8000',
    accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
}))

export async function requestEmailLoginCode(email: string, onError?: (msg: string) => void) {
    try {
        await api.loginWithEmailLoginMailPost({email:email})
        onError?.('验证邮件已发送，请在邮箱中查收')
        return true
    } catch (err: any) {
        if (err.response?.status === 422) {
            onError?.('Super Big Mistake!!!')
        } else if (err.response?.status === 404) {
            onError?.('用户不存在')
        } else if (err.response?.status === 401) {
            onError?.('邮箱未验证，请先验证邮箱')
        }
        return false
    }
}

export async function emailLoginCodeCheck(email: string, code: string, onError?: (msg: string) => void) {
    try {
        const response = await api.verifyLoginEmailCodeLoginMailCodePost({email: email, code: code})
        if(response == null) {
            onError?.("Super Big Mistake!!!")
            return false
        }
        if(response.status == 201 || response.status == 202) {
            onError?.("验证码未请求或已过期，请重新请求验证码")
            return false
        }else if(response.status == 203) {
            onError?.("验证码错误，请重新输入")
            return false
        }
        const token = response.data?.token
        if (token) {
            sessionStorage.setItem('token', token)
        } else {
            onError?.('登录失败：未获取到令牌')
            return false;
        }
        return true
    } catch (err: any) {
        if (err.response?.status === 422) {
            onError?.('Super Big Mistake!!!')
        } else if (err.response?.status === 404) {
            onError?.('用户不存在')
        }
        return false
    }
}