"""
Cloud Resource Manager - Real-World Banker's Algorithm Implementation
Manages cloud computing resources (CPU, Memory, GPU) for multiple services
using deadlock avoidance principles.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import copy
import os
from datetime import datetime
from typing import Optional

app = Flask(__name__, static_folder='static')
CORS(app)

# In-memory state (can be replaced with database)
class ResourceManager:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Default: Cloud infrastructure scenario
        # Resources: [CPU_Cores, Memory_GB, GPU_Units, Network_Bandwidth_Gbps]
        self.resource_names = ["CPU Cores", "Memory (GB)", "GPU Units", "Network (Gbps)"]
        self.available = [16, 64, 4, 10]  # Total available resources
        self.num_resources = len(self.available)
        
        # Services/processes with their maximum resource needs
        self.service_names = [
            "Web Server",
            "Database",
            "ML Training",
            "API Gateway",
            "Cache Service"
        ]
        self.num_processes = len(self.service_names)
        
        # Maximum resources each service can request
        self.maximum = [
            [8, 32, 0, 4],      # Web Server
            [6, 24, 0, 2],      # Database
            [12, 48, 4, 6],     # ML Training
            [4, 16, 0, 8],      # API Gateway
            [4, 20, 2, 3]       # Cache Service
        ]
        
        # Currently allocated resources
        self.allocation = [
            [2, 8, 0, 1],       # Web Server
            [3, 12, 0, 1],      # Database
            [0, 0, 0, 0],       # ML Training (not started)
            [1, 4, 0, 2],       # API Gateway
            [0, 4, 1, 1]        # Cache Service
        ]
        
        # Calculate need matrix
        self.need = [
            [self.maximum[i][j] - self.allocation[i][j] 
             for j in range(self.num_resources)]
            for i in range(self.num_processes)
        ]
        
        self.allocation_history = []
        self.request_log = []
        self.created_at = datetime.now().isoformat()
    
    def request_resources(self, service_id: int, request: list[int]) -> dict:
        """Request resources for a service using Banker's Algorithm"""
        if service_id >= self.num_processes:
            return {"success": False, "message": f"Invalid service ID: {service_id}"}
        
        if len(request) != self.num_resources:
            return {"success": False, "message": "Request length mismatch"}
        
        # Check if request exceeds maximum need
        for i in range(self.num_resources):
            if request[i] > self.need[service_id][i]:
                return {
                    "success": False, 
                    "message": f"{self.service_names[service_id]} exceeds maximum need for {self.resource_names[i]}"
                }
            
            if request[i] > self.available[i]:
                return {
                    "success": False,
                    "message": f"Insufficient {self.resource_names[i]} available. Requested: {request[i]}, Available: {self.available[i]}"
                }
        
        # Temporarily allocate resources
        self._allocate(service_id, request)
        
        # Check if resulting state is safe
        if self._is_safe_state():
            safe_sequence = self.get_safe_sequence()
            self.allocation_history.append({
                "action": "REQUEST",
                "service_id": service_id,
                "service_name": self.service_names[service_id],
                "resources": request,
                "resource_names": self.resource_names,
                "timestamp": datetime.now().isoformat()
            })
            self.request_log.append({
                "service_id": service_id,
                "request": request,
                "success": True,
                "status": "GRANTED",
                "timestamp": datetime.now().isoformat()
            })
            return {
                "success": True,
                "message": f"Resources granted to {self.service_names[service_id]}",
                "safe_sequence": safe_sequence,
                "safe_sequence_names": [self.service_names[i] for i in safe_sequence]
            }
        else:
            # Rollback allocation
            self._deallocate(service_id, request)
            self.request_log.append({
                "service_id": service_id,
                "request": request,
                "success": False,
                "status": "DENIED-UNSAFE",
                "timestamp": datetime.now().isoformat()
            })
            return {
                "success": False,
                "message": f"Request denied. Would lead to unsafe state (potential deadlock)"
            }
    
    def release_resources(self, service_id: int, release: list[int]) -> dict:
        """Release resources back to the pool"""
        if service_id >= self.num_processes:
            return {"success": False, "message": f"Invalid service ID: {service_id}"}
        
        for i in range(self.num_resources):
            if release[i] > self.allocation[service_id][i]:
                return {
                    "success": False,
                    "message": f"Cannot release more {self.resource_names[i]} than allocated"
                }
        
        self._deallocate(service_id, release)
        self.allocation_history.append({
            "action": "RELEASE",
            "service_id": service_id,
            "service_name": self.service_names[service_id],
            "resources": release,
            "resource_names": self.resource_names,
            "timestamp": datetime.now().isoformat()
        })
        self.request_log.append({
            "service_id": service_id,
            "request": release,
            "success": True,
            "status": "RELEASED",
            "timestamp": datetime.now().isoformat()
        })
        return {
            "success": True,
            "message": f"{self.service_names[service_id]} resources released"
        }
    
    def _allocate(self, service_id: int, resources: list[int]):
        for i in range(self.num_resources):
            self.available[i] -= resources[i]
            self.allocation[service_id][i] += resources[i]
            self.need[service_id][i] -= resources[i]
    
    def _deallocate(self, service_id: int, resources: list[int]):
        for i in range(self.num_resources):
            self.available[i] += resources[i]
            self.allocation[service_id][i] -= resources[i]
            self.need[service_id][i] += resources[i]
    
    def _is_safe_state(self) -> bool:
        work = copy.copy(self.available)
        finish = [False] * self.num_processes
        
        while True:
            found = False
            for p in range(self.num_processes):
                if not finish[p] and all(self.need[p][i] <= work[i] for i in range(self.num_resources)):
                    for i in range(self.num_resources):
                        work[i] += self.allocation[p][i]
                    finish[p] = True
                    found = True
            if not found:
                break
        
        return all(finish)
    
    def get_safe_sequence(self) -> list[int]:
        work = copy.copy(self.available)
        finish = [False] * self.num_processes
        safe_sequence = []
        
        while True:
            found = False
            for p in range(self.num_processes):
                if not finish[p] and all(self.need[p][i] <= work[i] for i in range(self.num_resources)):
                    for i in range(self.num_resources):
                        work[i] += self.allocation[p][i]
                    finish[p] = True
                    safe_sequence.append(p)
                    found = True
            if not found:
                break
        
        return safe_sequence if all(finish) else []
    
    def get_state(self) -> dict:
        safe_sequence = self.get_safe_sequence()
        return {
            "resource_names": self.resource_names,
            "available": self.available,
            "service_names": self.service_names,
            "num_processes": self.num_processes,
            "num_resources": self.num_resources,
            "maximum": self.maximum,
            "allocation": self.allocation,
            "need": self.need,
            "is_safe": self._is_safe_state(),
            "safe_sequence": safe_sequence,
            "safe_sequence_names": [self.service_names[i] for i in safe_sequence],
            "allocation_history": self.allocation_history,
            "request_log": self.request_log,
            "created_at": self.created_at
        }
    
    def load_scenario(self, scenario: str):
        """Load predefined real-world scenarios"""
        scenarios = {
            "cloud_computing": {
                "resource_names": ["CPU Cores", "Memory (GB)", "GPU Units", "Network (Gbps)"],
                "available": [16, 64, 4, 10],
                "service_names": ["Web Server", "Database", "ML Training", "API Gateway", "Cache Service"],
                "maximum": [
                    [8, 32, 0, 4],
                    [6, 24, 0, 2],
                    [12, 48, 4, 6],
                    [4, 16, 0, 8],
                    [4, 20, 2, 3]
                ],
                "allocation": [
                    [2, 8, 0, 1],
                    [3, 12, 0, 1],
                    [0, 0, 0, 0],
                    [1, 4, 0, 2],
                    [0, 4, 1, 1]
                ]
            },
            "database_connections": {
                "resource_names": ["Connections", "Memory (MB)", "IOPS", "CPU %"],
                "available": [50, 8192, 1000, 80],
                "service_names": ["Auth Service", "Analytics", "User API", "Reports", "Backup"],
                "maximum": [
                    [15, 2048, 300, 25],
                    [20, 4096, 500, 40],
                    [10, 1024, 200, 15],
                    [25, 3072, 400, 35],
                    [5, 512, 100, 10]
                ],
                "allocation": [
                    [5, 512, 100, 8],
                    [0, 0, 0, 0],
                    [3, 256, 50, 5],
                    [10, 1024, 150, 12],
                    [2, 128, 25, 3]
                ]
            },
            "manufacturing": {
                "resource_names": ["Robots", "Raw Materials", "Power (kW)", "Workers"],
                "available": [10, 100, 50, 20],
                "service_names": ["Assembly Line A", "Assembly Line B", "Quality Control", "Packaging", "Shipping"],
                "maximum": [
                    [4, 30, 15, 8],
                    [5, 40, 20, 10],
                    [2, 10, 5, 4],
                    [3, 25, 10, 6],
                    [2, 20, 8, 5]
                ],
                "allocation": [
                    [2, 15, 8, 4],
                    [0, 0, 0, 0],
                    [1, 5, 3, 2],
                    [1, 10, 4, 3],
                    [0, 5, 2, 1]
                ]
            },
            "hospital_system": {
                "resource_names": ["Beds", "Ventilators", "Staff", "Medicine Units"],
                "available": [50, 20, 30, 100],
                "service_names": ["ICU", "Emergency", "Surgery", "General Ward", "Pediatrics"],
                "maximum": [
                    [15, 10, 12, 30],
                    [20, 8, 15, 40],
                    [10, 5, 10, 20],
                    [25, 2, 8, 50],
                    [10, 3, 6, 25]
                ],
                "allocation": [
                    [8, 6, 8, 18],
                    [5, 2, 4, 10],
                    [0, 0, 0, 0],
                    [15, 1, 5, 30],
                    [3, 1, 2, 8]
                ]
            }
        }
        
        if scenario not in scenarios:
            return {"success": False, "message": f"Unknown scenario: {scenario}"}
        
        data = scenarios[scenario]
        self.resource_names = data["resource_names"]
        self.available = list(data["available"])
        self.service_names = data["service_names"]
        self.num_resources = len(self.available)
        self.num_processes = len(self.service_names)
        self.maximum = [list(row) for row in data["maximum"]]
        self.allocation = [list(row) for row in data["allocation"]]
        
        # Recalculate need
        self.need = [
            [self.maximum[i][j] - self.allocation[i][j] 
             for j in range(self.num_resources)]
            for i in range(self.num_processes)
        ]
        
        self.allocation_history = []
        self.request_log = []
        self.created_at = datetime.now().isoformat()
        
        return {"success": True, "message": f"Loaded scenario: {scenario}"}


# Initialize resource manager
resource_mgr = ResourceManager()


# API Routes
@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(resource_mgr.get_state())


@app.route('/api/request', methods=['POST'])
def request_resources():
    data = request.json
    service_id = data.get('service_id')
    resources = data.get('resources')
    
    if service_id is None or resources is None:
        return jsonify({"success": False, "message": "Missing service_id or resources"}), 400
    
    result = resource_mgr.request_resources(service_id, resources)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code


@app.route('/api/release', methods=['POST'])
def release_resources():
    data = request.json
    service_id = data.get('service_id')
    resources = data.get('resources')
    
    if service_id is None or resources is None:
        return jsonify({"success": False, "message": "Missing service_id or resources"}), 400
    
    result = resource_mgr.release_resources(service_id, resources)
    return jsonify(result)


@app.route('/api/scenario/<name>', methods=['POST'])
def load_scenario(name):
    result = resource_mgr.load_scenario(name)
    return jsonify(result)


@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    return jsonify({
        "scenarios": [
            {"id": "cloud_computing", "name": "Cloud Computing Resources", "description": "Manage CPU, Memory, GPU, and Network for cloud services"},
            {"id": "database_connections", "name": "Database Connection Pool", "description": "Allocate database connections, memory, IOPS, and CPU"},
            {"id": "manufacturing", "name": "Manufacturing Plant", "description": "Distribute robots, materials, power, and workers across production lines"},
            {"id": "hospital_system", "name": "Hospital Resource Management", "description": "Allocate beds, ventilators, staff, and medicine to departments"}
        ]
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    resource_mgr.reset()
    return jsonify({"success": True, "message": "System reset to default state"})


# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"  Cloud Resource Manager - Banker's Algorithm")
    print(f"  Server running at: http://localhost:{port}")
    print(f"  API endpoints:")
    print(f"    GET  /api/state         - Get current system state")
    print(f"    POST /api/request       - Request resources")
    print(f"    POST /api/release       - Release resources")
    print(f"    POST /api/scenario/<n>  - Load scenario")
    print(f"    GET  /api/scenarios     - List available scenarios")
    print(f"    POST /api/reset         - Reset system")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=True)
