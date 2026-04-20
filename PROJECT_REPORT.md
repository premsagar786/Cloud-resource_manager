# Cloud Resource Manager - Project Report

## 1. Introduction

The Cloud Resource Manager is a comprehensive web application that demonstrates the practical application of the **Banker's Algorithm** -- a classic deadlock avoidance algorithm originally developed by Edsger Dijkstra -- to modern resource management problems. While the Banker's Algorithm is traditionally taught in operating systems courses with abstract processes and resources, this project reimagines it for real-world scenarios including cloud infrastructure management, database connection pooling, manufacturing resource allocation, and hospital resource distribution.

## 2. Problem Statement

In distributed systems and cloud environments, multiple services compete for limited resources (CPU, memory, GPU, network bandwidth). Uncontrolled resource allocation can lead to **deadlocks** -- situations where services wait indefinitely for resources held by other services, causing system-wide failures. The Banker's Algorithm provides a mathematical approach to ensure that resource allocation always leaves the system in a "safe state" where all services can eventually complete their tasks.

## 3. Objectives

- Implement the Banker's Algorithm as a production-ready REST API
- Create an intuitive web dashboard for real-time resource monitoring
- Demonstrate the algorithm's applicability across diverse domains
- Provide interactive resource request/release functionality with immediate safety feedback
- Visualize resource utilization and safe execution sequences

## 4. System Architecture

### 4.1 Backend Architecture

The backend is built with **Flask**, a lightweight Python web framework, and consists of:

- **ResourceManager Class**: Core business logic implementing the Banker's Algorithm
  - `request_resources()`: Handles resource requests with safety verification
  - `release_resources()`: Returns resources to the pool
  - `_is_safe_state()`: Executes the safety algorithm
  - `get_safe_sequence()`: Computes the safe execution order
  - `load_scenario()`: Loads predefined real-world scenarios

- **REST API Endpoints**: Six endpoints for full CRUD operations on the resource state

### 4.2 Frontend Architecture

The frontend is a single-page application built with vanilla HTML, CSS, and JavaScript:

- **Dashboard Layout**: Card-based responsive design with dark theme
- **Real-time Rendering**: Automatic UI updates after every API call
- **Interactive Forms**: Dynamic resource input fields that adapt to the current scenario
- **Activity Logging**: Scrollable log with color-coded status indicators

### 4.3 Data Flow

```
User Action (Request/Release) → JavaScript → Flask API → ResourceManager → Banker's Algorithm → Response → UI Update
```

## 5. Algorithm Implementation

### 5.1 Key Data Structures

| Structure | Description | Example |
|-----------|-------------|---------|
| Available | Vector of available resources | [16, 64, 4, 10] |
| Maximum | Matrix of maximum needs per service | 5x4 matrix |
| Allocation | Matrix of currently allocated resources | 5x4 matrix |
| Need | Matrix of remaining needs (Maximum - Allocation) | 5x4 matrix |

### 5.2 Safety Algorithm

1. Initialize `Work = Available` and `Finish[i] = false` for all processes
2. Find a process `i` where `Finish[i] = false` and `Need[i] <= Work`
3. If found, set `Work = Work + Allocation[i]` and `Finish[i] = true`
4. Repeat until no such process exists
5. If all `Finish[i] = true`, the system is in a safe state

### 5.3 Resource Request Algorithm

1. If `Request <= Need`, continue; otherwise error (exceeds maximum)
2. If `Request <= Available`, continue; otherwise wait (insufficient resources)
3. **Temporarily** allocate: `Available -= Request`, `Allocation += Request`, `Need -= Request`
4. Run safety algorithm
5. If safe: commit allocation; if unsafe: rollback and deny request

## 6. Scenarios

### 6.1 Cloud Computing
- **Resources**: CPU Cores, Memory (GB), GPU Units, Network (Gbps)
- **Services**: Web Server, Database, ML Training, API Gateway, Cache Service
- **Use Case**: Managing compute resources across microservices

### 6.2 Database Connection Pool
- **Resources**: Connections, Memory (MB), IOPS, CPU %
- **Services**: Auth Service, Analytics, User API, Reports, Backup
- **Use Case**: Preventing connection exhaustion in database clusters

### 6.3 Manufacturing Plant
- **Resources**: Robots, Raw Materials, Power (kW), Workers
- **Services**: Assembly Line A, Assembly Line B, Quality Control, Packaging, Shipping
- **Use Case**: Optimizing production line resource distribution

### 6.4 Hospital System
- **Resources**: Beds, Ventilators, Staff, Medicine Units
- **Services**: ICU, Emergency, Surgery, General Ward, Pediatrics
- **Use Case**: Critical resource allocation during peak demand

## 7. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/state` | Get complete system state |
| POST | `/api/request` | Request resources for a service |
| POST | `/api/release` | Release resources from a service |
| POST | `/api/scenario/<name>` | Load a predefined scenario |
| GET | `/api/scenarios` | List all available scenarios |
| POST | `/api/reset` | Reset to default state |

## 8. User Interface Components

1. **Scenario Selector**: Switch between four real-world scenarios
2. **System State Cards**: Display available resources with utilization bars
3. **Status Badge**: Real-time SAFE/UNSAFE indicator with pulse animation
4. **Safe Sequence Display**: Shows the order of safe process execution
5. **Allocation Matrix Table**: Shows Allocation, Maximum, and Need matrices
6. **Resource Request Form**: Dynamic inputs for requesting/releasing resources
7. **Activity Log**: Timestamped log of all resource operations

## 9. Testing

### 9.1 Manual Testing Scenarios

- **Safe Request**: Request resources within need and available limits; verify GRANTED status
- **Unsafe Request**: Request that would lead to unsafe state; verify DENIED-UNSAFE status
- **Exceed Maximum**: Request more than the service's declared maximum; verify error
- **Insufficient Resources**: Request more than available; verify error
- **Resource Release**: Release allocated resources; verify available resources increase
- **Scenario Switching**: Load different scenarios; verify matrices update correctly
- **System Reset**: Reset to default; verify state returns to initial values

### 9.2 Safety Verification

The algorithm ensures that after every resource grant, there exists at least one sequence in which all services can complete their maximum resource needs without deadlock.

## 10. Technical Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Real-time state synchronization | Auto-refresh UI after every API call |
| Dynamic resource counts | Frontend adapts to variable resource/service counts |
| Rollback on unsafe state | Temporary allocation with rollback on safety failure |
| Responsive design | CSS Grid with auto-fit for all screen sizes |
| State management | Single source of truth in ResourceManager class |

## 11. Future Enhancements

- **Persistence**: SQLite/PostgreSQL database for state persistence
- **Authentication**: User roles and access control
- **WebSocket**: Real-time push notifications for state changes
- **Analytics Dashboard**: Historical resource usage graphs
- **Custom Scenarios**: User-defined scenario creation
- **Multi-tenant**: Support for multiple independent resource pools
- **Docker**: Containerized deployment
- **Rate Limiting**: API request throttling

## 12. Conclusion

The Cloud Resource Manager successfully bridges the gap between theoretical operating system concepts and practical resource management. By implementing the Banker's Algorithm in a modern web application with multiple real-world scenarios, it demonstrates that deadlock avoidance is not just an academic exercise but a relevant principle for designing robust distributed systems. The clean separation between the algorithm implementation and the presentation layer makes the codebase maintainable and extensible for future development.

## 13. References

1. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating System Concepts* (10th ed.). Wiley.
2. Dijkstra, E. W. (1965). *Cooperating Sequential Processes*. Technological University, Eindhoven.
3. Tanenbaum, A. S., & Bos, H. (2014). *Modern Operating Systems* (4th ed.). Pearson.
4. Flask Documentation: https://flask.palletsprojects.com/
