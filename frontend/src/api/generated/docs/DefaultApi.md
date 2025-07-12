# DefaultApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**checkFaceDataCheckFacePost**](#checkfacedatacheckfacepost) | **POST** /check_face/ | 人脸识别获取Token|
|[**getUserEmailGetUserEmailGet**](#getuseremailgetuseremailget) | **GET** /get_user_email/ | 获取用户邮箱信息|
|[**getUserInfoGetUserInfoGet**](#getuserinfogetuserinfoget) | **GET** /get_user_info/ | 获取用户信息|
|[**isMailVerifiedIsMailVerifiedGet**](#ismailverifiedismailverifiedget) | **GET** /is_mail_verified/ | 获取用户是否已验证邮箱|
|[**loginLoginPost**](#loginloginpost) | **POST** /login | 用户登录|
|[**loginWithEmailLoginMailPost**](#loginwithemailloginmailpost) | **POST** /login/mail/ | 通过邮箱登录|
|[**postFaceDataPostFacePost**](#postfacedatapostfacepost) | **POST** /post_face/ | 注册用户脸部数据|
|[**queryLogDetailLogDetailGet**](#querylogdetaillogdetailget) | **GET** /log_detail | 获取日志类型列表|
|[**queryLogsLogsGet**](#querylogslogsget) | **GET** /logs | 查询日志记录|
|[**registerRegisterPost**](#registerregisterpost) | **POST** /register | 用户注册|
|[**requestEmailVerificationVerifyEmailPut**](#requestemailverificationverifyemailput) | **PUT** /verify_email/ | 请求邮箱认证|
|[**rootGet**](#rootget) | **GET** / | Root|
|[**testAddLogsLogsTestGet**](#testaddlogslogstestget) | **GET** /logs/test | 添加日志记录|
|[**updateFaceDataUpdateFacePut**](#updatefacedataupdatefaceput) | **PUT** /update_face/ | 更新用户脸部数据|
|[**verifyEmailCodeVerifyEmailCodePost**](#verifyemailcodeverifyemailcodepost) | **POST** /verify_email_code/ | 邮箱认证验证码|
|[**verifyLoginEmailCodeLoginMailCodePost**](#verifyloginemailcodeloginmailcodepost) | **POST** /login/mail_code/ | 通过邮箱验证码登录|
|[**videoDetectVideoDetectPost**](#videodetectvideodetectpost) | **POST** /video_detect/ | 视频流道路病害检测|

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
|**402** | 活体检测失败 |  -  |
|**406** | 活体检测失败，有两人同时出现 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUserEmailGetUserEmailGet**
> UserEmail getUserEmailGetUserEmailGet()

获取用户邮箱信息

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.getUserEmailGetUserEmailGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**UserEmail**

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

# **loginWithEmailLoginMailPost**
> any loginWithEmailLoginMailPost(mailLoginRequest)

通过邮箱登录，请求验证码

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    MailLoginRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let mailLoginRequest: MailLoginRequest; //

const { status, data } = await apiInstance.loginWithEmailLoginMailPost(
    mailLoginRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mailLoginRequest** | **MailLoginRequest**|  | |


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
|**200** | 成功发送验证邮件 |  -  |
|**404** | 邮箱未注册 |  -  |
|**401** | 邮箱未验证 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **postFaceDataPostFacePost**
> any postFaceDataPostFacePost(imageModel)

注册用户脸部数据

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

const { status, data } = await apiInstance.postFaceDataPostFacePost(
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

# **queryLogDetailLogDetailGet**
> any queryLogDetailLogDetailGet()

获取日志类型列表  参数说明： - log_id：日志 ID，用于查询特定日志的详细信息  示例请求： /logs_detail?log_id=123e4567-e89b-12d3-a456-426614174000

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let logId: string; // (default to undefined)

const { status, data } = await apiInstance.queryLogDetailLogDetailGet(
    logId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **logId** | [**string**] |  | defaults to undefined|


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
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **queryLogsLogsGet**
> any queryLogsLogsGet()

根据查询条件返回日志记录，需要认证权限  参数说明： - log_type：允许根据日志类型过滤 - log_range：允许根据日志时间范围过滤，格式自定义 - limit：限制返回结果数量，默认为 10 - offset：指定从哪个位置开始返回结果  示例请求： /logs?log_type=ERROR&log_range=2025-07-01~2025-07-31&limit=20&offset=0

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let logType: string; //事件类型过滤 (optional) (default to undefined)
let logRange: string; //日志范围过滤，例如：2021-01-01~2021-12-31 (optional) (default to undefined)
let limit: number; //查询返回条数，默认返回 10 条 (optional) (default to 10)
let offset: number; //起始条数，默认从第 0 条记录开始 (optional) (default to 0)

const { status, data } = await apiInstance.queryLogsLogsGet(
    logType,
    logRange,
    limit,
    offset
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **logType** | [**string**] | 事件类型过滤 | (optional) defaults to undefined|
| **logRange** | [**string**] | 日志范围过滤，例如：2021-01-01~2021-12-31 | (optional) defaults to undefined|
| **limit** | [**number**] | 查询返回条数，默认返回 10 条 | (optional) defaults to 10|
| **offset** | [**number**] | 起始条数，默认从第 0 条记录开始 | (optional) defaults to 0|


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
|**200** | Successful Response |  -  |
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

# **testAddLogsLogsTestGet**
> any testAddLogsLogsTestGet()

测试添加日志记录的接口

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.testAddLogsLogsTestGet();
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

# **updateFaceDataUpdateFacePut**
> any updateFaceDataUpdateFacePut(imageModel)

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

const { status, data } = await apiInstance.updateFaceDataUpdateFacePut(
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

# **verifyLoginEmailCodeLoginMailCodePost**
> any verifyLoginEmailCodeLoginMailCodePost(mailCodeLoginRequest)

通过邮箱登录，检查验证码

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    MailCodeLoginRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let mailCodeLoginRequest: MailCodeLoginRequest; //

const { status, data } = await apiInstance.verifyLoginEmailCodeLoginMailCodePost(
    mailCodeLoginRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mailCodeLoginRequest** | **MailCodeLoginRequest**|  | |


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
|**200** | 邮箱登录成功 |  -  |
|**404** | 用户不存在 |  -  |
|**201** | 未请求验证码 |  -  |
|**202** | 验证码已过期 |  -  |
|**203** | 验证码错误 |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **videoDetectVideoDetectPost**
> VideoDetectResponse videoDetectVideoDetectPost(videoDetectRequest)

从上传的短视频中道路病害

### Example

```typescript
import {
    DefaultApi,
    Configuration,
    VideoDetectRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let videoDetectRequest: VideoDetectRequest; //

const { status, data } = await apiInstance.videoDetectVideoDetectPost(
    videoDetectRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **videoDetectRequest** | **VideoDetectRequest**|  | |


### Return type

**VideoDetectResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

