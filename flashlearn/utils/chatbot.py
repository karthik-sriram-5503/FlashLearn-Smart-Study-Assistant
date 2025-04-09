from langchain.chains import RetrievalQA
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

class Chatbot:
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = ChatOllama(model="deepseek-r1:8b", temperature=0.3)
        self.qa_chain = self._create_qa_chain()
        
    def _get_custom_prompt(self):
        """Define and return the custom prompt template."""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are an educational assistant designed to help students understand their textbooks. Follow these guidelines:\n"
                "1. Answer questions using only the information from the uploaded PDFs.\n"
                "2. Use simple, clear language suitable for a students.\n"
                "3. If the answer isn't in the documents, say: 'I cannot find relevant information in the provided documents.'\n"
                "4. Do not speculate, assume, or invent information.\n"
                "5. Maintain a professional tone and organize responses clearly (e.g., bullet points, step-by-step explanations).\n"
                "6. Encourage follow-up questions by asking if further clarification is needed.\n"
                "7. Provide examples to clarify concepts when helpful.\n"
                "8. Keep answers concise, focused, and exam-friendly."
            ),
            HumanMessagePromptTemplate.from_template(
                "Context:\n{context}\n\n"
                "Question: {question}\n\n"
                "Provide a precise and well-structured answer based on the context above. Ensure your response is easy to understand, includes examples where necessary, and is formatted in a way that students can use it for exams. If applicable, ask if the student needs further clarification."
            )
        ])
    
    def _create_qa_chain(self):
        """Create a QA chain for the chatbot."""
        return RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": self._get_custom_prompt()}
        )
    
    def get_response(self, query):
        """Get a response from the chatbot."""
        try:
            response = self.qa_chain.invoke({"query": query})
            # Remove <think> section if present
            result = response["result"].split("</think>")[-1].strip()
            return result
        except Exception as e:
            return f"Error: {str(e)}"