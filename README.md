# Cloud Resource Manager - Banker's Algorithm

A modern web application that implements the **Banker's Algorithm** for deadlock avoidance, applied to real-world resource management scenarios including cloud computing, database connections, manufacturing plants, and hospital systems.

## Features

- **Real-time Dashboard** - Monitor resource availability, allocation, and system safety status
- **Interactive Resource Management** - Request and release resources with instant safety verification
- **4 Real-World Scenarios**:
  - Cloud Computing (CPU, Memory, GPU, Network)
  - Database Connection Pool (Connections, Memory, IOPS, CPU)
  - Manufacturing Plant (Robots, Materials, Power, Workers)
  - Hospital System (Beds, Ventilators, Staff, Medicine)
- **Safe Sequence Visualization** - See the order in which services can complete without deadlock
- **Activity Logging** - Track all resource requests, grants, denials, and releases
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Dark Theme UI** - Modern, clean interface with resource utilization bars

## Tech Stack

- **Backend**: Python 3, Flask, Flask-CORS
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Algorithm**: Banker's Algorithm for Deadlock Avoidance

## Installation

```bash
# Clone the repository
git clone https://github.com/premsagar786/Cloud-resource_manager.git
cd Cloud-resource_manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The server will start at `http://localhost:5000`

## API Documentation

### GET `/api/state`
Returns the current system state including resource availability, allocation matrix, maximum matrix, need matrix, safety status, and safe sequence.

### POST `/api/request`
Request resources for a service.

```json
{
  "service_id": 0,
  "resources": [2, 4, 0, 1]
}
```

### POST `/api/release`
Release resources back to the pool.

```json
{
  "service_id": 0,
  "resources": [1, 2, 0, 0]
}
```

### POST `/api/scenario/<name>`
Load a predefined scenario. Available scenarios:
- `cloud_computing`
- `database_connections`
- `manufacturing`
- `hospital_system`

### GET `/api/scenarios`
List all available scenarios with descriptions.

### POST `/api/reset`
Reset the system to the default cloud computing scenario.

## How the Banker's Algorithm Works

The Banker's Algorithm is a resource allocation and deadlock avoidance algorithm that:

1. **Checks Request Validity** - Ensures the request does not exceed the process's maximum need
2. **Checks Availability** - Ensures sufficient resources are available
3. **Simulates Allocation** - Temporarily allocates resources to check if the resulting state is safe
4. **Safety Algorithm** - Finds a safe sequence where all processes can complete
5. **Commits or Rolls Back** - If safe, grants the request; otherwise, denies it to prevent deadlock

## Project Structure

```
Banker_algo/
├── app.py              # Flask backend with Banker's Algorithm
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── PROJECT_REPORT.md  # Comprehensive project report
└── static/
    ├── index.html     # Frontend dashboard
    ├── style.css      # Dark theme styles
    └── script.js      # Frontend JavaScript
```

## License

MIT License
