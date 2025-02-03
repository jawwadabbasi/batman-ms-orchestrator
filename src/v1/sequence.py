class Sequence:

    def Tasks(action):

        tasks = []

        if action == 'batcave-secure':
            tasks = Sequence.SecureBatcave()

        if action == 'batmobile-deploy':
            tasks = Sequence.DeployBatmobile()

        if action == 'batcomputer-scan':
            tasks = Sequence.ScanWithBatcomputer()

        tasks.extend(Sequence.StandardProtocol())

        return tasks

    def SecureBatcave():
        
        return [
            {
                'Action': 'batcave-lockdown',
                'Display': 'Activating Batcave lockdown',
                'Microservice': {
                    'Service': 'batcode-ms-security',
                    'Endpoint': '/api/v1/Batcave/Lockdown',
                    'Method': 'POST',
                    'RequestBody': [
                        'IntrusionSensors', 
                        'ReinforcedDoors'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 1,
                    'MergeIntoPayload': 1,
                    'MergeIntoMeta': 1
                }
            },
            {
                'Action': 'batcave-surveillance',
                'Display': 'Scanning Batcave perimeter',
                'Microservice': {
                    'Service': 'batcode-ms-detective',
                    'Endpoint': '/api/v1/Surveillance/Scan',
                    'Method': 'GET',
                    'RequestBody': [
                        'ThermalVision', 
                        'MotionSensors'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 0,
                    'MergeIntoPayload': 0,
                    'MergeIntoMeta': 0
                }
            }
        ]

    def DeployBatmobile():
        
        return [
            {
                'Action': 'batmobile-engine-check',
                'Display': 'Running Batmobile diagnostics',
                'Microservice': {
                    'Service': 'batcode-ms-vehicles',
                    'Endpoint': '/api/v1/Batmobile/Diagnostics',
                    'Method': 'POST',
                    'RequestBody': [
                        'FuelLevels', 
                        'TirePressure'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 0,
                    'MergeIntoPayload': 0,
                    'MergeIntoMeta': 0
                }
            },
            {
                'Action': 'batmobile-launch',
                'Display': 'Deploying Batmobile',
                'Microservice': {
                    'Service': 'batcode-ms-vehicles',
                    'Endpoint': '/api/v1/Batmobile/Deploy',
                    'Method': 'POST',
                    'RequestBody': [
                        'Destination', 
                        'StealthMode'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 1,
                    'MergeIntoPayload': 1,
                    'MergeIntoMeta': 1
                }
            }
        ]

    def ScanWithBatcomputer():
        
        return [
            {
                'Action': 'batcomputer-data-retrieve',
                'Display': 'Retrieving Gotham crime data',
                'Microservice': {
                    'Service': 'batcode-ms-intel',
                    'Endpoint': '/api/v1/Batcomputer/CrimeScan',
                    'Method': 'GET',
                    'RequestBody': [
                        'CrimeReports', 
                        'FacialRecognition'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 1,
                    'MergeIntoPayload': 0,
                    'MergeIntoMeta': 1
                }
            },
            {
                'Action': 'batcomputer-hack',
                'Display': 'Hacking into criminal networks',
                'Microservice': {
                    'Service': 'batcode-ms-intel',
                    'Endpoint': '/api/v1/Hack/CriminalNetworks',
                    'Method': 'POST',
                    'RequestBody': [
                        'TargetList', 
                        'EncryptionBypass'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 1,
                    'MergeIntoPayload': 1,
                    'MergeIntoMeta': 1
                }
            }
        ]

    def StandardProtocol():
        
        return [
            {
                'Action': 'bat-signal-activate',
                'Display': 'Activating the Bat-Signal',
                'Microservice': {
                    'Service': 'batcode-ms-alerts',
                    'Endpoint': '/api/v1/BatSignal/Activate',
                    'Method': 'POST',
                    'RequestBody': [
                        'EmergencyCode'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 1,
                    'MergeIntoPayload': 0,
                    'MergeIntoMeta': 1
                }
            },
            {
                'Action': 'broadcast-alert',
                'Display': 'Notifying the Justice League',
                'Microservice': {
                    'Service': 'batcode-ms-broadcast',
                    'Endpoint': '/api/v1/Alert/Send',
                    'Method': 'POST',
                    'RequestBody': [
                        'RecipientList', 
                        'UrgencyLevel'
                    ]
                },
                'Meta': {
                    'IncidentRequired': 1,
                    'PollingRequired': 0,
                    'MergeIntoPayload': 0,
                    'MergeIntoMeta': 0
                }
            }
        ]