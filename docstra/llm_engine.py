from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI

DEFAULT_SYSTEM_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)


class DocstraLLMEngine:
    def __init__(self, retriever, system_prompt=DEFAULT_SYSTEM_PROMPT):
        self.llm = ChatOpenAI()
        self.system_prompt = system_prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
            ]
        )
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(retriever, self.question_answer_chain)

    def run_query(self, question):
        return self.rag_chain.invoke({"input": question})
