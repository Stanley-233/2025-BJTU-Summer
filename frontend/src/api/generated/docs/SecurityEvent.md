# SecurityEvent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [optional] [default to undefined]
**log_level** | [**LogLevel**](LogLevel.md) | 日志级别 | [optional] [default to undefined]
**link_username** | **string** |  | [optional] [default to undefined]
**event_type** | [**EventType**](EventType.md) | 事件类型 | [default to undefined]
**description** | **string** |  | [default to undefined]
**timestamp** | **string** | 事件发生时间 | [default to undefined]

## Example

```typescript
import { SecurityEvent } from './api';

const instance: SecurityEvent = {
    id,
    log_level,
    link_username,
    event_type,
    description,
    timestamp,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
