"""Query endpoints for Docstra API."""

from fastapi import APIRouter, Depends, HTTPException

from docstra.core import (
    ILLMChain,
    ISessionManager,
    IContextManager, 
    IRetriever,
    IIndexer
)
from docstra.api.dependencies import (
    get_llm_chain,
    get_session_manager,
    get_context_manager,
    get_retriever,
    get_indexer,
    handle_exceptions
)
from docstra.api.models import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
@handle_exceptions(status_code=500, error_message="Error processing query")
async def query_endpoint(
    request: QueryRequest,
    llm_chain: ILLMChain = Depends(get_llm_chain),
    session_manager: ISessionManager = Depends(get_session_manager),
    context_manager: IContextManager = Depends(get_context_manager),
    retriever: IRetriever = Depends(get_retriever),
    indexer: IIndexer = Depends(get_indexer),
) -> QueryResponse:
    """Query the codebase with a natural language question.

    Args:
        request: The query request.
        llm_chain: The LLM chain service.
        session_manager: The session manager service.
        context_manager: The context manager service.
        retriever: The retriever service.
        indexer: The indexer service.

    Returns:
        The query response.

    Raises:
        HTTPException: If an error occurs during query execution.
    """
    # Get or create session
    if request.session_id:
        try:
            session = session_manager.get_session(request.session_id)
        except Exception as e:
            raise HTTPException(
                status_code=404, detail=f"Session not found: {str(e)}"
            )
    else:
        session = session_manager.get_or_create_session()

    # Get context
    context = context_manager.get_context(session)

    # Add specific context files if provided
    context_docs = []
    if request.context_files:
        for file_path in request.context_files:
            # Get or index the file
            doc = indexer.get_or_index_file(file_path)
            if doc:
                context_docs.append(doc)

    # Retrieve relevant documents if no specific files provided
    if not context_docs:
        context_docs = retriever.retrieve(request.query, session=session)

    # Run the query
    response = llm_chain.run(
        query=request.query,
        context=context,
        documents=context_docs,
        temperature=request.temperature,
    )

    return QueryResponse(
        response=response,
        session_id=session.id,
    )