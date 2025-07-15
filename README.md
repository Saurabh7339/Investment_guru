Investment Guru is an intelligent, AI-driven financial assistant that helps users make smarter investment decisions using cutting-edge Generative AI and retrieval-augmented generation (RAG) techniques.

At its core, Investment Guru combines LangChain and LangGraph to orchestrate complex, multi-step reasoning workflows for generating tailored recommendations. It leverages ChromaDB for storing and querying vector embeddings, enabling fast and relevant semantic search across financial documents, reports, and client data.

Key features include:

🔍 Context-aware recommendations — Uses RAG pipelines to ground LLM output in up-to-date market data and personalized client profiles.

⚙️ Pluggable LLM backend — Supports multiple language models like Ollama (Llama3), Gemini, or OpenAI, with robust fallback and retry logic.

🗃️ Semantic vector store — Powered by ChromaDB to handle document chunking, embeddings, and fast similarity search.

🔗 Composable workflows — Built with LangGraph to define investment recommendation pipelines as reusable, modular graph steps.

Stack highlights:

FastAPI for the backend API

LangChain & LangGraph for advanced LLM orchestration

ChromaDB for vector storage and retrieval

Ollama / Gemini / OpenAI for local or cloud-based language models

RAG pattern for trustworthy, explainable AI insights

Investment Guru empowers financial advisors and retail investors alike by delivering actionable insights with transparency and explainability — all backed by modern GenAI best practices.

