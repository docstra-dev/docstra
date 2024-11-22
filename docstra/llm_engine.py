from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, BasePromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

DEFAULT_SYSTEM_PROMPT = ("""
    You are an expert software developer with detailed knowledge about a codebase. Use the following pieces of context to answer the question. If asked about the location of a code snippet, try to provide the file path with line numbers. If you don't know the answer, say that you don't know. Keep the answer concise.
    \n\n
    "{context}"
""")

DEFAULT_DOCUMENT_PROMPT = ("""
    Type: {content_type}, Source file: {source}, Start line: {start_line}, End line: {end_line}\nSource code:{page_content}
""")


def initialize_llm(system_prompt=DEFAULT_SYSTEM_PROMPT, document_prompt=DEFAULT_DOCUMENT_PROMPT):
    """Initializes the ChatOpenAI model and sets up the prompt template."""
    llm = ChatOpenAI(
        temperature=0.0,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    document_prompt = PromptTemplate(template=document_prompt, input_variables=[
        "content_type", "source", "start_line", "end_line", "page_content"
    ])

    return llm, prompt, document_prompt

def create_question_answer_chain(llm, prompt, document_prompt):
    """Creates a question-answer chain using the given LLM and prompt template."""
    return create_stuff_documents_chain(llm, prompt, document_prompt=document_prompt)

def create_rag_chain(retriever, question_answer_chain):
    """Creates a retrieval-augmented generation chain."""
    return create_retrieval_chain(retriever, question_answer_chain)

def run_query(retriever, question, system_prompt=DEFAULT_SYSTEM_PROMPT, document_prompt=DEFAULT_DOCUMENT_PROMPT):
    """Runs a query using a retrieval-augmented generation chain."""
    llm, prompt, document_prompt = initialize_llm(system_prompt, document_prompt)
    question_answer_chain = create_question_answer_chain(llm, prompt, document_prompt)
    rag_chain = create_rag_chain(retriever, question_answer_chain)
    return rag_chain.invoke({"input": question})
