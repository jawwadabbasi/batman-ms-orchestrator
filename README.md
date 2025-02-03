## How the Batman Orchestrator Works

In the Gotham Operations Hub, when actions like 'deploy-batmobile,' 'summon-batsignal,' or 'secure-wayne-manor' are initiated, a request is created in the Batman Orchestrator service along with the sequential tasks needed to process that request. These tasks represent the individual steps required to complete the mission, ensuring that Batman’s operations are executed efficiently.

For example, deploying the Batmobile involves several steps:

1. **Check fuel and diagnostics** (Call to Batcave AI service)
2. **Open Batcave exit** (Call to Security system)
3. **Engage stealth mode** (Call to Batmobile systems)
4. **Deploy Batmobile to location** (Call to Batcomputer navigation)
5. **Confirm arrival and readiness** (Call to Gotham tracking system)

The Batman Orchestrator ensures that these calls are made and that each step receives the payload it needs to be processed. The main payload is dynamically updated with new values returned from the services, whether through direct API responses or periodic polling.


### Key Services Integrated with Batman Orchestrator
If you are working on any of the following Bat-services and are making changes to their controllers, please notify the Bat-Signal, as the orchestrator depends on them:

- **batcode-ms-batcave** (AI Systems and Diagnostics)
- **batcode-ms-waynetech** (Gadgets and Armory Management)
- **batcode-ms-batmobile** (Vehicle Deployment System)
- **batcode-ms-batsignal** (Gotham Emergency Alerts)
- **batcode-ms-security** (Wayne Manor and Batcave Security)
- **batcode-ms-intel** (Villain Tracking and Intelligence Gathering)

### Example Orchestrated Task Sequence: Deploying the Batmobile

```json
[
    {
        "Action": "batmobile-check-systems",
        "Display": "Running Batmobile diagnostics",
        "Microservice": {
            "Service": "batcode-ms-batcave",
            "Endpoint": "/api/v1/Batmobile/Diagnostics",
            "Method": "GET",
            "RequestBody": [
                "FuelLevel", 
                "SystemCheck"
            ]
        }
    },
    {
        "Action": "batmobile-open-exit",
        "Display": "Opening Batcave exit",
        "Microservice": {
            "Service": "batcode-ms-security",
            "Endpoint": "/api/v1/Batcave/Exit",
            "Method": "POST",
            "RequestBody": [
                "ExitCode"
            ]
        }
    },
    {
        "Action": "batmobile-engage-stealth",
        "Display": "Engaging stealth mode",
        "Microservice": {
            "Service": "batcode-ms-batmobile",
            "Endpoint": "/api/v1/Stealth/Activate",
            "Method": "POST",
            "RequestBody": [
                "StealthMode"
            ]
        }
    },
    {
        "Action": "batmobile-navigate",
        "Display": "Deploying Batmobile to location",
        "Microservice": {
            "Service": "batcode-ms-batmobile",
            "Endpoint": "/api/v1/Navigate",
            "Method": "POST",
            "RequestBody": [
                "Destination"
            ]
        }
    },
    {
        "Action": "batmobile-arrival-check",
        "Display": "Confirming Batmobile arrival",
        "Microservice": {
            "Service": "batcode-ms-intel",
            "Endpoint": "/api/v1/Tracking/Confirm",
            "Method": "GET",
            "RequestBody": [
                "VehicleID"
            ]
        }
    }
]
```

### Explore the Code
To get a better understanding of how the orchestrator works and which Bat-services it interacts with, check out the `sequence.py` file. This will provide insights into how mission workflows are structured and executed dynamically.

Welcome to the Batman Orchestrator – Gotham’s most powerful automated operations system!