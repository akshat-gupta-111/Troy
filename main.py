'''
Main Execution pipeline
'''

import uuid
import json 
import logging 
from pprint import pprint
from dotenv import load_dotenv

load_dotenv(override=True)

from backend.src.graph.workflow import app

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("troy-runner")

def run_cli_simulation():
    print("\n Pipeline start-----")
    session_id = str(uuid.uuid4())

    logger.info(f"Starting Audit Session : {session_id}")

    initial_inputs = {
        "video_url" : "https://youtu.be/dT7S75eYhcQ",
        "video_id" : f"vid_{session_id[:8]}",
        "compliance_results" : [],
        "errors" : [],
    }

    print("\n ------- Initializing the Workflowe ----")

    print(f"Input Payload: {json.dumps(initial_inputs, indent=2)}")

    try:
        final_state = app.invoke(initial_inputs)

        print("----- Workflow Execution Complete ----")

        print("\n Compliance Report : ")
        print(f"Video Id {final_state.get('video_id')}")
        print(f"Status : {final_state.get("final_status")}")
        print("\n [Violations Detected]")
        results = final_state.get('compliance_results', [])

        if results:
            for issue in results:
                print(f"[{issue.get('severity')}] : [{issue.get('category')}] : [{issue.get('description')}] :")
        else:
            print("NO Violation detected....")
            
        print("\n Final Summary")
        print(final_state.get('final_report'))

    except Exception as e:
        logger.error(f"Workflow wxecution falise : {str(e)}")
        raise e

if __name__ == "__main__":
    run_cli_simulation()

