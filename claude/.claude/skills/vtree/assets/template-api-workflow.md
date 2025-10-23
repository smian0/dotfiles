# API Workflow Template

Ready-to-use template for API request/response workflows with authentication and error handling.

```
[1]     **API_Endpoint** [📥 request] → [🔐 auth → (2) | ❌ unauthorized → (5)]
[2]     Auth_Success [✅ token ← (1)] → [🛡️ validate → (3)]
[3]     Request_Handler [📥 validated ← (2)] → [⚡ process → (3.1,3.2)]
[3.1]   ├─ Business_Logic [📥 data ← (3)] → [🧠 compute → (4)]
[3.2]   └─ *External_Service* [🌐 fetch ← (3)] → [⏳ await → (4)]
[4]     Response_Builder [📥 results ← (3.1)+(3.2)]
        → [✅ success → (6) | ❌ error → (5)]
[5]     Error_Handler [📥 error ← (1,4)] → [🔧 format → (6)]
[6]     **Response** [📥 final ← (4)+(5)] → [📤 send → (END)]
```

## Customization Guide

### 1. Replace Authentication Method
```
# OAuth
[1] API_Endpoint [📥 request] → [🔐 oauth → (2) | ❌ denied → (5)]

# JWT
[1] API_Endpoint [📥 request] → [🔐 jwt_verify → (2) | ❌ invalid → (5)]

# API Key
[1] API_Endpoint [📥 request] → [🔐 key_check → (2) | ❌ forbidden → (5)]
```

### 2. Add Rate Limiting
```
[1]     **API_Endpoint** [📥 request] → [🛡️ rate_limit → (1.1) | ⚠️ throttle → (5)]
[1.1]   └─ Check_Auth [🔐 auth ← (1)] → [✅ ok → (2) | ❌ denied → (5)]
```

### 3. Add Caching Layer
```
[2]     Auth_Success [✅ token ← (1)] → [💾 check_cache → (2.1,3)]
[2.1]   └─ Cache_Hit [✅ found] → [📤 cached → (6)]
[3]     Request_Handler [📥 validated ← (2)] → [⚡ process → (3.1,3.2)]
```

### 4. Add Logging/Monitoring
```
[3]     Request_Handler [📥 validated ← (2)] → [⚡ process → (3.1,3.2,3.3)]
[3.1]   ├─ Business_Logic [📥 data ← (3)] → [🧠 compute → (4)]
[3.2]   ├─ *External_Service* [🌐 fetch ← (3)] → [⏳ await → (4)]
[3.3]   └─ Logger [📡 track ← (3)] → [💾 logged]
```

### 5. Add Retry Logic for External Service
```
[3.2]   └─ *External_Service* [🌐 fetch ← (3)]
        → [✅ success → (4) | ❌ failed → (3.2.1)]
[3.2.1]     └─ Retry_Handler [🔧 retry ← (3.2)]
            → [🔄 attempt → (3.2) | ❌ give_up → (5)]
```

## Common API Patterns

### RESTful CRUD
```
[1] Router [📥 http_request] → [🎯 route → (2.1,2.2,2.3,2.4)]
[2.1] ├─ **GET** [📥 id] → [💾 read → (3)]
[2.2] ├─ **POST** [📥 data] → [💾 create → (3)]
[2.3] ├─ **PUT** [📥 id+data] → [💾 update → (3)]
[2.4] └─ **DELETE** [📥 id] → [💾 remove → (3)]
[3] Response [📥 result ← (2.1)+(2.2)+(2.3)+(2.4)] → [📤 json]
```

### GraphQL Resolver
```
[1] GraphQL_Server [📥 query] → [🔍 parse → (2)]
[2] Resolver [📥 parsed ← (1)] → [🎯 route → (2.1,2.2)]
[2.1] ├─ Query_Resolver [📥 query ← (2)] → [💾 fetch → (3)]
[2.2] └─ Mutation_Resolver [📥 mutation ← (2)] → [💾 update → (3)]
[3] Result_Builder [📥 data ← (2.1)+(2.2)] → [📤 response]
```

### Webhook Handler
```
[1] **Webhook_Receiver** [📥 event] → [🛡️ verify_signature → (2) | ❌ invalid → (5)]
[2] Signature_Valid [✅ verified ← (1)] → [📊 parse_payload → (3)]
[3] Event_Router [📥 payload ← (2)] → [🎯 dispatch → (3.1,3.2,3.3)]
[3.1] ├─ Handler_A [📥 event_a ← (3)] → [⚡ process → (4)]
[3.2] ├─ Handler_B [📥 event_b ← (3)] → [⚡ process → (4)]
[3.3] └─ Default_Handler [📥 other ← (3)] → [⚡ log → (4)]
[4] Acknowledge [📥 done ← (3.1)+(3.2)+(3.3)] → [📤 200_ok]
[5] Error_Response [📥 error ← (1)] → [📤 401_unauthorized]
```
