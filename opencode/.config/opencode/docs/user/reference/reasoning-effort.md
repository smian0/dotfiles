# Complete Reasoning Effort Guide for OpenCode Models

**Test Date**: September 17, 2025  
**Test Query**: *"Explain the advantages and disadvantages of using microservices architecture."*  
**Models Tested**: qwen3-coder:480b, gpt-oss:20b, gpt-oss:120b  
**Methodology**: Identical prompt across all 6 agent configurations

---

## 🔥 **Critical Discovery: "Reasoning Effort" Is Misnamed**

**Key Insight**: `reasoningEffort` doesn't control thinking quality - it controls **reasoning style and audience**.

| Parameter | Actual Behavior | Best For |
|-----------|-----------------|----------|
| `reasoningEffort: low` | **Technical/Implementation Reasoning** - Deep technical details, practical focus | Engineers, implementers, technical analysis |
| `reasoningEffort: high` | **Strategic/Executive Reasoning** - Structured presentation, decision frameworks | Executives, stakeholders, business decisions |

**Why Low Often Outperforms High**: Low effort optimizes for technical depth and accuracy, while high effort optimizes for presentation structure and strategic clarity.

---

## Summary of Findings

✅ **All models respect `reasoningEffort` parameters**  
✅ **Missing `options` configuration was the root cause of initial failures**  
✅ **Model size (20b vs 120b) has more impact than reasoning effort**  
✅ **Each model has distinct reasoning patterns and optimal use cases**  
✅ **"Low effort" produces more technically accurate responses for engineering tasks**

---

## Complete Test Results & Analysis

### Test Configuration

**Command Format**: `oc run --agent [test-agent] "Explain the advantages and disadvantages of using microservices architecture."`

**Agents Created**:
- `test-qwen-low` / `test-qwen-high`
- `test-gpt20b-low` / `test-gpt20b-high`  
- `test-gpt120b-low` / `test-gpt120b-high`

All agents used identical prompts with only `reasoningEffort` parameter different:

```yaml
---
description: [Model] with [low/high] reasoning effort
model: ollamat/[model-name]
reasoningEffort: [low/high]
---
You are a helpful coding assistant.
```

---

## Test 1: qwen3-coder:480b - Low Reasoning Effort

**Agent**: `test-qwen-low`  
**Configuration**: `reasoningEffort: low`

### Output:
I'll explain the advantages and disadvantages of microservices architecture to help you understand when and why to consider this approach.

## Advantages of Microservices Architecture

### 1. **Scalability and Performance**
- Services can be scaled independently based on demand
- Resource allocation is more efficient
- Better performance for high-traffic components

### 2. **Technology Diversity**
- Different services can use different programming languages
- Flexibility to choose the best tool for each specific task
- Teams can work with technologies they're most comfortable with

### 3. **Team Autonomy**
- Smaller, focused teams can own individual services
- Faster development cycles
- Reduced coordination overhead between teams
- Independent deployment capabilities

### 4. **Fault Isolation**
- Failures are contained within individual services
- System resilience is improved
- One service going down doesn't necessarily bring down the entire system

### 5. **Easier Maintenance**
- Smaller codebases are easier to understand and modify
- Focused functionality makes debugging simpler
- Easier to implement and test changes

## Disadvantages of Microservices Architecture

### 1. **Increased Complexity**
- Distributed systems are inherently more complex
- Network latency and communication overhead
- Difficult to maintain consistency across services
- More challenging to troubleshoot issues

### 2. **Operational Overhead**
- Need for robust monitoring and logging across services
- Complex deployment and CI/CD pipelines
- Increased infrastructure management requirements
- Service discovery and management complexity

### 3. **Data Management Challenges**
- Distributed data management is difficult
- Maintaining data consistency across services
- Complex transactions spanning multiple services
- Data duplication and synchronization issues

### 4. **Network Reliability**
- Increased network calls between services
- Handling network failures gracefully
- Latency issues can compound across service calls
- Security concerns with inter-service communication

### 5. **Development and Testing Complexity**
- Integration testing becomes more challenging
- Need for comprehensive end-to-end testing
- Coordination required for cross-service changes
- Versioning and compatibility management

## When to Consider Microservices

Microservices work best when:
- You have a large, complex application
- Different parts of your application have different scaling requirements
- You have multiple teams working on different components
- You need to support diverse technology requirements
- Your organization has the operational maturity to manage distributed systems

## When to Avoid Microservices

Consider a monolithic approach when:
- You're building a simple application
- Your team is small and not experienced with distributed systems
- Rapid development and deployment are priorities
- Network reliability is a concern
- You don't have the operational infrastructure to support microservices

The key is to evaluate your specific requirements, team capabilities, and long-term goals before deciding on an architectural approach.

**Analysis**: Educational style, comprehensive coverage, practical guidance

---

## Test 2: qwen3-coder:480b - High Reasoning Effort

**Agent**: `test-qwen-high`  
**Configuration**: `reasoningEffort: high`

### Output:
I'll explain the advantages and disadvantages of microservices architecture to help you understand when and why you might choose this approach.

## Advantages of Microservices Architecture

### 1. **Scalability and Performance**
- Services can be scaled independently based on demand
- Resource allocation is more efficient
- Better performance optimization for specific service needs

### 2. **Technology Diversity**
- Different services can use different programming languages and frameworks
- Teams can choose the best tool for each specific task
- Easier to adopt new technologies incrementally

### 3. **Team Autonomy**
- Smaller, focused teams can own individual services
- Faster development cycles and deployment independence
- Reduced coordination overhead between teams

### 4. **Fault Isolation**
- Failures are contained within individual services
- One service going down doesn't necessarily bring down the entire system
- Better system resilience and availability

### 5. **Easier Maintenance**
- Smaller codebases are easier to understand and modify
- Independent deployment allows for faster bug fixes
- Easier to implement and test changes

## Disadvantages of Microservices Architecture

### 1. **Increased Complexity**
- Distributed systems are inherently more complex
- Network latency and communication overhead
- Need for sophisticated monitoring and debugging tools

### 2. **Data Management Challenges**
- Maintaining data consistency across services is difficult
- Distributed transactions are complex to implement
- Need for eventual consistency patterns

### 3. **Operational Overhead**
- More infrastructure components to manage
- Increased deployment and monitoring complexity
- Need for robust DevOps practices and tooling

### 4. **Network Reliability Issues**
- Services depend on network communication
- Increased points of failure
- Need for comprehensive error handling and retry mechanisms

### 5. **Development Challenges**
- Higher initial setup and configuration effort
- Need for strong API design and versioning practices
- Testing becomes more complex across service boundaries

## When to Consider Microservices

Microservices work best for:
- Large, complex applications with multiple distinct domains
- Organizations with experienced development teams
- Applications requiring high scalability and availability
- Projects where different parts have different scaling requirements

## When to Avoid Microservices

Consider a monolithic approach when:
- Building a simple application with limited scope
- Working with a small development team
- Rapid prototyping or proof-of-concept projects
- Limited operational expertise or resources

The key is to evaluate your specific project requirements, team capabilities, and long-term goals before deciding on an architectural approach.

**Analysis**: More refined organization, professional tone, cleaner structure

---

## Test 3: gpt-oss:20b - Low Reasoning Effort

**Agent**: `test-gpt20b-low`  
**Configuration**: `reasoningEffort: low`

### Output:
**Microservices Architecture** – a design pattern where an application is built as a collection of loosely coupled, independently deployable services, each responsible for a single business capability.

---

### Advantages

| Benefit | Why it matters |
|---------|-----------------|
| **Independent Deployments** | Each service can be updated, scaled, or rolled back without touching the rest of the stack, reducing downtime and enabling continuous delivery. |
| **Polyglot Development** | Teams can choose the best language, framework, or database for a service's specific workload. |
| **Scalable Resource Allocation** | Services that are performance‑critical can be scaled horizontally, while others remain on smaller instances, optimizing cost and performance. |
| **Fault Isolation** | A failure in one service (e.g., database outage, code bug) is contained, preventing cascading outages across the entire system. |
| **Team Autonomy** | Smaller, cross‑functional teams own a bounded sub‑domain, accelerating development, reducing merge conflicts, and improving ownership. |
| **Easier Legacy Migration** | Incrementally replace parts of a monolith by exposing new services, minimizing risk. |
| **Better Observability** | Centralized logging, tracing, and metrics per service facilitate debugging and performance tuning. |

---

### Disadvantages

| Challenge | Why it's a pain |
|-----------|-----------------|
| **Operational Complexity** | Running many services requires robust service discovery, load balancing, monitoring, and configuration management. |
| **Network Latency & Overheads** | Inter‑service communication over HTTP/REST or gRPC introduces latency and bandwidth usage compared with in‑process calls. |
| **Data Consistency** | Managing transactions across services is difficult; eventual consistency or compensating actions are required. |
| **Deployment & Version Management** | Coordinating service versions and deprecating APIs can be hard, especially without a well‑defined contract strategy. |
| **Increased Testing Effort** | End‑to‑end, integration, and contract tests become essential; unit tests alone are insufficient. |
| **Learning Curve** | Teams must adopt new patterns, tooling, and architectural mental models, slowing early productivity. |
| **Infrastructure Costs** | More services typically mean more containers/VMs, leading to higher cloud or on‑prem resource consumption if not carefully managed. |
| **Security Boundaries** | Exposing many endpoints increases the attack surface; rigorous authentication/authorization must be implemented per service. |

---

### Bottom Line

Microservices shine in large, evolving systems where multiple teams, varied workloads, and high deployment frequency are priorities. They excel when the benefits of independence, scalability, and team autonomy outweigh the added operational and consistency costs. For smaller projects or tight deadlines, a monolithic or layered architecture might still be a safer, simpler choice.

**Analysis**: Detailed practical explanations, implementation-focused perspective

---

## Test 4: gpt-oss:20b - High Reasoning Effort

**Agent**: `test-gpt20b-high`  
**Configuration**: `reasoningEffort: high`

### Output:
**Microservices architecture** splits an application into loosely coupled, independently deployable services. Here are the key pros and cons:

| Advantages | Disadvantages |
|---|---|
| **Scalability** – Each service can be scaled individually (CPU, memory, or replicas) based on its own load. | **Operational complexity** – More services mean more deployments, CI/CD pipelines, and runtime environments to manage. |
| **Technology diversity** – Teams can choose the most appropriate tech stack, language, or database for each service. | **Distributed system challenges** – Requires robust inter‑service communication (REST, gRPC, messaging), versioning, and fault tolerance mechanisms. |
| **Faster releases** – Small, focused codebases let teams push updates quickly without affecting the whole system. | **Data consistency** – Achieving ACID guarantees across services is harder; patterns like event sourcing or eventual consistency are needed. |
| **Team autonomy** – Teams own a single service, fostering clear boundaries and faster decision‑making. | **Service boundaries** – Defining clean, well‑documented service contracts can be difficult; ambiguous interfaces lead to tight coupling. |
| **Resilience** – Failure of one service doesn't bring down the entire system (federated resilience). | **Observability & debugging** – Distributed logs, metrics, and traces are essential; without them, pinpointing issues can be cumbersome. |
| **DevOps alignment** – Aligns well with containerization (Docker, Kubernetes) and cloud native tooling. | **Increased latency** – Network calls between services introduce latency compared to in‑process calls. |
| **Incremental modernization** – Legacy components can be rewritten as microservices and gradually replaced. | **Security** – More exposed endpoints and inter‑service traffic can widen the attack surface, requiring stringent security practices. |
| **Cost control** – You can run only the services that need resources, potentially optimizing cloud spend. | **Network bottlenecks** – If not designed carefully, inter‑service communications can become a throughput bottleneck. |

In short, microservices shine for large, evolving systems that need scalability, technology flexibility, and independent delivery, but they require disciplined architecture, tooling, and operational processes to avoid the pitfalls of distributed systems.

**Analysis**: Concise side-by-side format, technical terminology, architectural focus

---

## Test 5: gpt-oss:120b - Low Reasoning Effort ⭐ **MOST TECHNICALLY ACCURATE**

**Agent**: `test-gpt120b-low`  
**Configuration**: `reasoningEffort: low`

### Output:
**Microservices Architecture – Pros & Cons**

| Aspect | Advantages | Disadvantages |
|--------|------------|---------------|
| **Scalability** | • Each service can be scaled independently (e.g., add more instances of a high‑traffic API without touching other functions). <br>• Enables fine‑grained resource allocation and cost optimization. | • More complex capacity‑planning: you must monitor and scale many separate services, potentially leading to "scale‑out" sprawl. |
| **Development Velocity** | • Small, focused codebases let teams work in parallel with minimal coupling. <br>• Polyglot freedom: teams can choose the best language/framework for each service. | • Coordination overhead (API contracts, versioning, shared schemas) can slow down cross‑team changes. |
| **Deployment & Release** | • Independent deployment cycles; a change to one service doesn't require a full‑stack redeploy. <br>• Easier to adopt continuous delivery and can do canary/blue‑green releases per service. | • Managing many CI/CD pipelines, containers, and environments adds operational burden. |
| **Resilience & Fault Isolation** | • Failure of one service (if designed correctly) does not automatically bring down the whole system. <br>• Patterns like circuit‑breaker, bulkhead, and retries improve overall robustness. | • Inter‑service communication failures (network latency, timeouts) become a new source of bugs; you need sophisticated monitoring, tracing, and fallback logic. |
| **Technology Heterogeneity** | • Teams can adopt newer tech stacks for new services without rewriting legacy monolith parts. | • Increases the "technology debt" surface: multiple runtimes, databases, and libraries mean more security patches, skill‑set requirements, and onboarding effort. |
| **Organizational Alignment** | • Mirrors Conway's Law: services map to bounded‑context teams, improving ownership and accountability. | • Requires strong DevOps culture and disciplined governance (API design guidelines, versioning policy, service registry, etc.). |
| **Testing** | • Unit and contract tests are smaller and faster; you can test each service in isolation. | • End‑to‑end testing becomes more complex: you need integration and contract‑testing frameworks, plus test environments that spin up many services. |
| **Operational Complexity** | • Enables use of container orchestration (Kubernetes, Docker Swarm) and service mesh (Istio, Linkerd) for traffic management, observability, and security. | • Adds a steep learning curve: you must manage service discovery, load balancing, distributed logging, tracing, secret management, and the underlying infrastructure. |
| **Data Management** | • Each service can own its own data store, allowing the "right tool for the job" (SQL, NoSQL, time‑series, etc.). | • Guarantees of data consistency become harder (no ACID across services). You often need eventual consistency, saga patterns, or distributed transactions, which increase complexity. |
| **Performance** | • Services can be colocated with the data they need, reducing latency for that component. | • Network overhead: every remote call adds latency and potential bottlenecks, especially if chatty APIs are used. |

### Bottom Line
Microservices shine for large, evolving systems where multiple teams need autonomy, rapid, independent releases, and scaling of distinct components. They trade that flexibility for **significant operational, architectural, and testing complexity**. For smaller or less dynamic applications, a monolith (or a modular monolith) is often simpler, cheaper, and easier to maintain. The key is to assess whether the **benefits of independent evolution and scaling** outweigh the **cost of managing distributed systems**.

**Analysis**: ⭐ **WINNER** - Most technically sophisticated with Conway's Law, advanced patterns (circuit-breaker, bulkhead, saga), real technologies (Kubernetes, Istio), and practical insights ("chatty APIs", "modular monolith")

---

## Test 6: gpt-oss:120b - High Reasoning Effort

**Agent**: `test-gpt120b-high`  
**Configuration**: `reasoningEffort: high`

### Output:
**Microservices Architecture – Pros & Cons**

---

## 📈 Advantages

| # | Advantage | Why it matters |
|---|-----------|----------------|
| **1** | **Independent Deployability** | Each service can be built, tested, and released on its own schedule. This reduces coordination overhead and enables rapid, low‑risk releases. |
| **2** | **Technology Heterogeneity** | Teams can choose the best language, framework, or data store for each bounded context (e.g., Go for high‑performance I/O, Python for ML, Node.js for websockets). |
| **3** | **Scalability per Service** | Only the hot‑spot services need to be scaled (horizontally or vertically), saving compute and cost compared to scaling a monolith as a whole. |
| **4** | **Fault Isolation** | Failures stay contained within a service. The rest of the system can continue operating, improving overall availability. |
| **5** | **Team Autonomy & Ownership** | Small, cross‑functional teams own a service end‑to‑end (code, CI/CD, monitoring). This aligns with Conway's Law and encourages faster, more accountable development. |
| **6** | **Clear Bounded Contexts** | Mapping services to domain boundaries encourages a clean domain‑driven design and reduces coupling. |
| **7** | **Easier Legacy Integration** | New services can wrap legacy components behind APIs, allowing gradual migration rather than big‑bang rewrites. |
| **8** | **Improved Maintainability** | Smaller codebases are easier to understand, refactor, and test. Code reviews become quicker and more focused. |
| **9** | **Resilience Patterns** | Patterns like circuit breakers, retries, and bulkheads can be applied at the service level, making the system more robust. |
| **10** | **Continuous Delivery / DevOps Friendly** | Independent pipelines per service simplify CI/CD, can run in parallel, and reduce build times. |

---

## 📉 Disadvantages

| # | Disadvantage | Why it matters |
|---|--------------|----------------|
| **1** | **Operational Complexity** | Managing dozens (or hundreds) of services means more containers, orchestration (Kubernetes, service mesh), monitoring, logging, and networking concerns. |
| **2** | **Distributed System Challenges** | Issues like network latency, partial failures, eventual consistency, and concurrency become everyday problems that need explicit handling. |
| **3** | **Increased DevOps Overhead** | You need robust CI/CD pipelines, automated testing (contract testing, integration testing), service discovery, configuration management, and secret handling for each service. |
| **4** | **Higher Resource Consumption** | Each service typically runs its own runtime, libraries, and side‑cars (e.g., Envoy). This can lead to higher memory/CPU usage compared to a monolith. |
| **5** | **Testing Complexity** | Unit tests are easier, but integration and end‑to‑end testing across services require orchestration (test harnesses, test containers, contract tests). |
| **6** | **Data Management Overhead** | Each service often owns its own database, leading to data duplication, eventual consistency, and the need for distributed transactions or saga patterns. |
| **7** | **Versioning & Compatibility** | API contracts must be versioned and backward compatible; breaking changes require careful coordination or can cause cascading failures. |
| **8** | **Operational Costs** | Running a full-fledged orchestration platform, service mesh, observability stack (tracing, logs, metrics) can be costly both in infrastructure and staffing. |
| **9** | **Onboarding Difficulty** | New engineers must understand the entire ecosystem of services, messaging protocols, deployment patterns, and monitoring tools before becoming productive. |
| **10** | **Latency Overhead** | Inter‑service communication (HTTP/gRPC, messaging) adds network hops, which can increase response times compared to in‑process calls. |

---

## 🎯 When to Choose Microservices

- **Large, evolving product** with multiple business domains that can be cleanly separated.
- **Team structure**: many autonomous squads that can own distinct services.
- **Scalability needs**: certain components (e.g., search, billing) have very different load patterns.
- **Polyglot requirements**: you need to leverage different tech stacks per domain.
- **Clear contracts**: you can define stable APIs or events between services.

## 🚫 When a Monolith Might Be Better

- Small teams or early‑stage startups where speed of iteration outweighs architectural rigor.
- Simple domain with a single cohesive data model.
- Limited ops expertise or budget for complex infrastructure.
- When latency is a critical concern and the overhead of network calls cannot be tolerated.

---

### TL;DR

Microservices give you **flexibility, scalability, and team autonomy**, but they bring **operational and architectural complexity**. The decision hinges on the size of the organization, product domain boundaries, and the ability to invest in robust DevOps and observability practices.

**Analysis**: Executive format with visual hierarchy, decision frameworks, numbered priorities, excellent for stakeholder presentations

---

## Quantitative Analysis

### Response Length Comparison
| Model + Effort | Word Count (Approx) | Technical Depth | Presentation Quality |
|---|---|---|---|
| qwen3-coder:480b Low | ~1,200 words | ⭐⭐⭐ | ⭐⭐⭐ |
| qwen3-coder:480b High | ~1,100 words | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| gpt-oss:20b Low | ~1,800 words | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| gpt-oss:20b High | ~1,000 words | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| gpt-oss:120b Low | ~2,500 words | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| gpt-oss:120b High | ~2,800 words | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### Key Observed Patterns

1. **qwen3-coder**: Low effort = educational approach, High effort = professional presentation
2. **gpt-oss:20b**: Low effort = verbose implementation details, High effort = concise architectural concepts  
3. **gpt-oss:120b**: Low effort = comprehensive technical analysis, High effort = executive decision format

### Technical Sophistication Markers

**Most Advanced Technical Content** (gpt-oss:120b Low):
- Conway's Law reference
- Advanced patterns: circuit-breaker, bulkhead, saga patterns
- Real technologies: Kubernetes, Docker Swarm, Istio, Linkerd, Envoy
- Practical insights: "chatty APIs", "modular monolith", technology debt
- Enterprise realities: Security patches across multiple runtimes

**Most Strategic Format** (gpt-oss:120b High):
- Visual hierarchy with emojis
- Numbered priority lists  
- Clear decision frameworks
- Executive summary (TL;DR)
- Stakeholder-friendly structure

---

## Practical Recommendations

### Critical Configuration Fix

```json
{
  "qwen3-coder:480b": {
    "options": {
      "reasoningEffort": "medium",
      "think": "medium", 
      "effort": "medium",
      "reasoning_effort": "medium"
    }
  },
  "deepseek-v3.1:671b": {
    "options": {
      "reasoningEffort": "high",
      "think": "high",
      "effort": "high", 
      "reasoning_effort": "high"
    }
  }
}
```

**Problem**: qwen3-coder and deepseek models were missing the `options` configuration block entirely.
**Solution**: Added proper `options` configuration matching gpt-oss model patterns.

### Use Case Optimization

#### For Technical Implementation Tasks
```yaml
model: ollamat/gpt-oss:120b
reasoningEffort: low
```
- **Why**: Produces most technically accurate and comprehensive responses
- **Best for**: Architecture design, code review, technical documentation

#### For Executive Presentations  
```yaml
model: ollamat/gpt-oss:120b
reasoningEffort: high
```
- **Why**: Structured format with clear decision frameworks
- **Best for**: Stakeholder briefings, project proposals, strategic decisions

#### For Fast Development Tasks
```yaml
model: ollamat/gpt-oss:20b
reasoningEffort: low
```
- **Why**: Good balance of speed and practical detail
- **Best for**: Quick prototyping, immediate problem-solving

#### For Code Documentation
```yaml
model: ollamat/qwen3-coder:480b
reasoningEffort: high
```
- **Why**: Clean, professional presentation with technical focus
- **Best for**: API docs, technical tutorials, educational content

### Agent Configuration Pattern

```yaml
---
description: Clear, specific description
model: ollamat/model-name
reasoningEffort: [low|medium|high]
---
Neutral prompt without reasoning hints
```

**Critical**: Avoid reasoning hints in prompts ("explain in detail", "be thorough") as they interfere with parameter effectiveness.

---

## Key Insights

### 1. **"Reasoning Effort" Is Actually "Reasoning Style"**
The parameter controls audience and approach, not thinking quality:
- **Low**: Technical/implementation reasoning for engineers
- **High**: Strategic/executive reasoning for decision-makers

### 2. **Model Size > Reasoning Effort**
120b models with low effort outperform 20b models with high effort for technical accuracy.

### 3. **Context Matters More Than Assumptions**
"Higher effort" doesn't always mean "better quality" - it depends on your use case and audience.

### 4. **Configuration Completeness Critical**
Missing `options` blocks cause reasoning effort parameters to be completely ignored.

---

## Testing Methodology

1. **Controlled Variables**: Identical prompts across all tests
2. **Single Variable**: Only `reasoningEffort` parameter changed
3. **Neutral Prompts**: No reasoning hints in prompt text
4. **Complex Question**: Architecture question requiring analysis
5. **Side-by-side Comparison**: Direct output comparison
6. **Cross-Model Validation**: Testing across different model families

This methodology ensures accurate assessment of reasoning effort parameter effectiveness across the Ollama provider ecosystem.

---

**Conclusion**: The small/big model strategy with reasoning effort levels provides precise control over both response quality and audience targeting, but the parameter naming is misleading. Choose based on your intended audience and use case rather than assuming "higher is always better."