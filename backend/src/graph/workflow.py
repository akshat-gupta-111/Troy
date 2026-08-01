'''
This module defines the DAG, that ochestrate the video compliance audit process.
connect the nodes using the Stategraph from LangGraph
'''

from langgraph.graph import StateGraph, END

from backend.src.graph.state import VideoAuditState

from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)


def create_graph():
    '''
    Constructs and Compiles the LangGraph workflow
    Returns:
        Compiled Graph : a runnable graph object.
    '''

    #intitialize the graph with state schema
    workflow = StateGraph(VideoAuditState)
    #add the nodes
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    workflow.set_entry_point("indexer")

    workflow.add_edge("indexer", "auditor")

    workflow.add_edge("auditor", END)

    app = workflow.compile()

    return app


app = create_graph()