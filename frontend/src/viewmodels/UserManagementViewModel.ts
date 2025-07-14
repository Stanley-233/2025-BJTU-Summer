import { Configuration, DefaultApi } from '../api/generated'
import type { UserWithEmail, UserType } from '../api/generated'

declare const sessionStorage: any

const api = new DefaultApi(new Configuration({
  basePath: 'http://127.0.0.1:8000',
  accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
}))

// 获取所有用户
export async function fetchAllUsers(onError?: (msg: string) => void): Promise<UserWithEmail[] | null> {
  try {
    const response = await api.getUsersWithEmailUsersGet()
    return response.data
  } catch (err: any) {
    onError?.('获取用户列表失败' + err.message)
    return null
  }
}

// 修改用户权限
export async function updateUserPermission(
  username: string,
  newType: UserType,
  onError?: (msg: string) => void,
  onSuccess?: (msg: string) => void
): Promise<boolean> {
  try {
    await api.changeUserPermissionUserChangePermissionPut(username, newType)
    onSuccess?.('修改权限成功')
    return true
  } catch (err: any) {
    onError?.('修改权限失败')
    return false
  }
}
