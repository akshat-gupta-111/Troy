import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

# schema

class ComplianceIssue(TypedDict):
    category : str
    description : str
    severity : str   # CRITICAL | WARNING
    timestamp : Optional[str]

# global graph state

class VideoAuditState(TypedDict):
    '''
    Defines the Data Schema for langgraph execution content
    '''

    #input
    video_url : str
    video_id : str

    #ingestion
    local_file_path : Optional[str]
    video_metadata : Dict[str, Any]
    transcript : Optional[str]
    ocr_text : List[str]

    #analysis output

    compliance_results : Annotated[List[ComplianceIssue], operator.add]

    final_status : str
    final_report : str

    # system observability - timeouts, errors
    errors : Annotated[List[str], operator.add]



