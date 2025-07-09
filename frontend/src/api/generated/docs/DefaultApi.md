# DefaultApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**checkFaceDataCheckFacePost**](#checkfacedatacheckfacepost) | **POST** /check_face/ | 人脸识别获取Token|
|[**getUserInfoGetUserInfoGet**](#getuserinfogetuserinfoget) | **GET** /get_user_info/ | 获取用户信息|
|[**isMailVerifiedIsMailVerifiedGet**](#ismailverifiedismailverifiedget) | **GET** /is_mail_verified/ | 获取用户是否已验证邮箱|
|[**loginLoginPost**](#loginloginpost) | **POST** /login | 用户登录|
|[**putFaceDataPostFacePut**](#putfacedatapostfaceput) | **PUT** /post_face/ | 上传用户脸部数据|
|[**registerRegisterPost**](#registerregisterpost) | **POST** /register | 用户注册|
|[**requestEmailVerificationVerifyEmailPut**](#requestemailverificationverifyemailput) | **PUT** /verify_email/ | 请求验证邮箱|
|[**rootGet**](#rootget) | **GET** / | Root|
|[**verifyEmailCodeVerifyEmailCodePost**](#verifyemailcodeverifyemailcodepost) | **POST** /verify_email_code/ | 验证邮箱验证码|

# **checkFaceDataCheckFacePost**
> any checkFaceDataCheckFacePost(userCheckFaceRequest)

Base64 人脸识别匹配，识别成功后返回用户登录Token

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    UserCheckFaceRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let userCheckFaceRequest: UserCheckFaceRequest; //

const { status, data } = await apiInstance.checkFaceDataCheckFacePost(
    userCheckFaceRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userCheckFaceRequest** | **UserCheckFaceRequest**|  | |


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 人脸成功识别 |  -  |
|**404** | 用户不存在或人脸数据不存在 |  -  |
|**401** | 认证错误 |  -  |
|**403** | 人脸数据不匹配 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUserInfoGetUserInfoGet**
> User getUserInfoGetUserInfoGet()

获取当前用户信息

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.getUserInfoGetUserInfoGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**User**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **isMailVerifiedIsMailVerifiedGet**
> any isMailVerifiedIsMailVerifiedGet()

获取用户是否已验证邮箱

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.isMailVerifiedIsMailVerifiedGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 返回验证状态 |  -  |
|**404** | 用户不存在 |  -  |
|**401** | 认证错误 |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **loginLoginPost**
> any loginLoginPost(userLoginRequest)

用户登录

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    UserLoginRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let userLoginRequest: UserLoginRequest; //

const { status, data } = await apiInstance.loginLoginPost(
    userLoginRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userLoginRequest** | **UserLoginRequest**|  | |


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 登录成功 |  -  |
|**404** | 用户不存在 |  -  |
|**403** | 密码错误 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **putFaceDataPostFacePut**
> any putFaceDataPostFacePut(imageModel)

更新用户脸部数据

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    ImageModel
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let imageModel: ImageModel; //

const { status, data } = await apiInstance.putFaceDataPostFacePut(
    imageModel
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **imageModel** | **ImageModel**|  | |


### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 成功更改 |  -  |
|**404** | 用户不存在 |  -  |
|**401** | 认证错误 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **registerRegisterPost**
> any registerRegisterPost(userRegisterRequest)

用户注册，返回注册成功消息

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    UserRegisterRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let userRegisterRequest: UserRegisterRequest; //

const { status, data } = await apiInstance.registerRegisterPost(
    userRegisterRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userRegisterRequest** | **UserRegisterRequest**|  | |


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 注册成功 |  -  |
|**400** | 用户名已存在 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **requestEmailVerificationVerifyEmailPut**
> any requestEmailVerificationVerifyEmailPut()

生成验证码并发送到用户邮箱

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.requestEmailVerificationVerifyEmailPut();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 验证码已发送 |  -  |
|**404** | 用户不存在 |  -  |
|**401** | 认证错误 |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rootGet**
> any rootGet()


### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.rootGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verifyEmailCodeVerifyEmailCodePost**
> any verifyEmailCodeVerifyEmailCodePost()

验证用户提交的验证码

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let code: string; // (default to undefined)

const { status, data } = await apiInstance.verifyEmailCodeVerifyEmailCodePost(
    code
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **code** | [**string**] |  | defaults to undefined|


### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | 邮箱验证成功 |  -  |
|**404** | 用户不存在 |  -  |
|**401** | 认证错误 |  -  |
|**201** | 未请求验证码 |  -  |
|**202** | 验证码已过期 |  -  |
|**203** | 验证码错误 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

