# ⚡ FlashLearn — AI-Powered Study Assistant

FlashLearn is an intelligent learning platform designed to revolutionize the way you study. Upload your PDFs—books, scanned notes, or study materials—and let FlashLearn do the heavy lifting. It automatically summarizes chapters, generates flashcards, and chatbot assistant to help you grasp and retain knowledge faster.

> 📘 Learn smart. 📌 Revise better. 🚀 Remember forever.

---

## ✨ Features

- 📄 **PDF Input**  
  Upload any book, notes, or document in PDF format.

- 🧠 **Content Detection & TOC Generation**  
  Automatically detects or generates a table of contents from the document.

- 📚 **Chapter-Wise Summarization**  
  Pick a chapter and receive a crisp, AI-generated summary.

- 🃏 **Flashcard Generation**  
  Create Q&A style flashcards from any topic for effective revision.

- 🤖 **RAG-Based Chatbot Assistant**  
  Chat with an intelligent assistant that uses Retrieval-Augmented Generation to answer questions based on your uploaded PDF content.

- 🚀 **STAR Attention Integration**  
  Efficiently processes long documents using NVIDIA's STAR Attention mechanism.

---

## 🛠️ Tech Stack

- **Frontend**: Html, css, Streamlit 
- **Backend**: Python (Django) 
- **AI/NLP**: Transformers, PyTorch, NVIDIA STAR Attention    

---

## 🚧 How It Works

1. **Upload PDF** ➝ FlashLearn scans and detects Table of Contents (ToC) or auto-generates one.
2. **Select Chapter** ➝ AI summarizes the selected chapter concisely.
3. **Summarizer the topic** ➝ Get the summarization based on the selected chapter
4. **Generate Flashcards** ➝ Get instant flashcards based on the selected chapter.
5. **Chat with Your Document** ➝ Ask questions to a chatbot trained specifically on your uploaded content using RAG. 

---

## 💬 About the RAG Chatbot

The chatbot uses **Retrieval-Augmented Generation**, combining semantic search over document chunks with a powerful LLM. Ask deep or specific questions and get answers grounded in the actual content of your PDF.

---

## 🧪 Running Locally

```bash
# Clone the repository
git clone https://github.com/perarulalan15/FlashLearn-Smart-Study-Assistant.git
cd flashlearn
python manage.py runserver

## 👥 Contributors

|        Name        |                 GitHub                  | 
|--------------------|-----------------------------------------|
| Karthik Sriram B A | (https://github.com/karthik-sriram-5503)|
| Aashifa Parveen A  | (https://github.com/Aashifaabdul)       |
