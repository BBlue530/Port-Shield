import time
import requests
from IPLogger import logger
from Variables import HEADERS
from ProgramMonitoring.HandleBadProgram import  kill_program, quarantine_program

###############################################################################################################

def check_scan_status(analysis_id, path_to_program):
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    
    retries = 0
    while retries < 3:
        try:
            response = requests.get(url, headers=HEADERS)
            json_response = response.json()
            
            if response.status_code == 200:
                status = json_response.get("data", {}).get("attributes", {}).get("status")
                if status == "completed":
                    print(f"[i] Scan completed: {path_to_program}")
                    message = f"[i] Scan completed: {path_to_program}"
                    logger(message)
                    results = json_response.get("data", {}).get("attributes", {}).get("results", {})
                    print(f"[i] Scan results: {results}")
                    message = f"[i] Scan results: {results}"
                    logger(message)
                    detected = sum([1 for engine in results.values() if engine["category"] == "malicious"])

                    if detected > 0:
                        print(f"[!] WARNING: {path_to_program} detected!")
                        message = f"[!] WARNING: {path_to_program} detected!"
                        logger(message)
                        kill_program(path_to_program)
                        quarantine_program(path_to_program)
                    else:
                        print(f"[i] Program {path_to_program} is safe.")
                        message = f"[i] Program {path_to_program} is safe."
                        logger(message)
                    return
                else:
                    print(f"[i] Retrying Scan: {path_to_program}")
                    retries += 1
                    time.sleep(60)
            else:
                print(f"[!] ERROR scan status: {response.status_code}")
                message = f"[!] ERROR scan status: {path_to_program}: {response.status_code}"
                logger(message)
                return
            
        except Exception as e:
            print(f"[!] ERROR: {e}")
            message = f"[!] ERROR: {e}"
            logger(message)
            retries += 1
            time.sleep(10)

###############################################################################################################

def submit_file_for_scan(path_to_program):
    url = "https://www.virustotal.com/api/v3/files"
    try:
        with open(path_to_program, "rb") as file:
            files = {'file': (path_to_program, file)}
            response = requests.post(url, headers=HEADERS, files=files)
        
        if response.status_code == 200:
            json_response = response.json()
            
            if 'data' in json_response and 'id' in json_response['data']:
                analysis_id = json_response['data']['id']
                print(f"[i] File submitted successfully. Analysis ID: {analysis_id}")
                return analysis_id
            else:
                print(f"[!] ERROR: Response did not have data: {json_response}")
                return None
        else:
            print(f"[!] ERROR Submit File: Status Code: {response.status_code}")
            print(f"[i] Response: {response.json()}")
            return None
    except Exception as e:
        print(f"[!] ERROR submitting: {path_to_program}: {e}")
        return None
    
###############################################################################################################