import logging
import os
from time import sleep
from typing import Dict, List,TypedDict
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM

from app.models.client import InvestmentRecommendation
logger = logging.getLogger("app")


class RecommendationState(TypedDict):
    client_id: int
    client_data: Dict
    analysis: Dict
    context: str
    recommendations: List[Dict]
    risk_analysis: Dict


class RecommendationService:
    def __init__(self, rag_service,max_retries=2):
        self.rag_service = rag_service
        self.max_retries = max_retries
        self.llm = self._initialize_llm()
        # self.llm = OllamaLLM(model="llama3") 
        self.workflow = self._create_workflow()
    

    def _initialize_llm(self):
        """Initialize LLM with retry logic"""
        # from langchain_ollama import Ollama
        retries = 0
        while retries < self.max_retries:
            try:
                llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro-latest",
                temperature=0.7,
                google_api_key="AIzaSyABcWgJEdcYA6_iAzKRNQKyVkwTyum9H3g")
                
                # Test connection
                llm.invoke("Test connection")
                return llm
            except Exception as e:
                retries += 1
                # logger.warning(f"LLM connection failed (attempt {retries}/{self.max_retries}): {e}")
                sleep(2 ** retries)  # Exponential backoff
                print("Failed to connect to Ollama after multiple attempts")
            # logger.warning(f"Gemini initialization failed: {gemini_error}")
            
            # Fallback to Ollama
            try:
                # from langchain_ollama import Ollama
                return OllamaLLM(model="llama3", timeout=120)
            except Exception as ollama_error:
                # logger.error(f"Ollama initialization failed: {ollama_error}")
                raise ConnectionError("Failed to initialize any LLM backend")
    def _create_workflow(self):
        workflow = StateGraph(RecommendationState)
        
        # Define nodes
        workflow.add_node("analyze_client", self.analyze_client)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("generate_recommendations", self.generate_recommendations)
        workflow.add_node("assess_risk", self.assess_risk)
        workflow.add_node("finalize_output", self.finalize_output)
        
        # Define edges
        workflow.add_edge("analyze_client", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "assess_risk")
        workflow.add_edge("assess_risk", "finalize_output")
        
        # Set entry point
        workflow.set_entry_point("analyze_client")
        
        return workflow.compile()
    
    def analyze_client(self, state: Dict):
        """Analyze client data and prepare for context retrieval"""
        client_data = state["client_data"]
        analysis = {
            "key_factors": {
                "risk_tolerance": client_data["risk_tolerance"],
                "investment_horizon": client_data["investment_horizon"],
                "goals": client_data["investment_goals"],
                "current_portfolio": client_data["portfolio"]
            }
        }
        logger.info(f"in function analyze_client to get the analysis , analysis is {analysis}")
        return {"analysis": analysis}
    
    def retrieve_context(self, state: Dict):
        """Retrieve relevant context using RAG"""
        client_data = state["client_data"]
        logger.info(f"in function retrieve_context before executing the context for recommendation")
        context = self.rag_service.get_context_for_recommendation(client_data)
        logger.info(f"the retrieved context is {context}")
        return {"context": context}
    
    def generate_recommendations(self, state: Dict):
        """Generate initial recommendations based on client data and context"""
        client_data = state["client_data"]
        context = state["context"]
        
        prompt = f"""
        You are a financial advisor creating personalized investment recommendations.
        
        Client Profile:
        {json.dumps(client_data, indent=2)}
        
        Relevant Market Context:
        {context}
        
        Generate 3-5 specific investment recommendations tailored to this client.
        For each recommendation, include:
        - Asset class
        - Specific investment (if applicable)
        - Allocation percentage
        - Rationale
        - Expected risk level
        - Time horizon
        
        Structure the output as a JSON list.
        """
        logger.info(f"in function generate_recommendations before executing the llm")
        logger.info(f"printing the prompt here before calling the llm --> {prompt} and also context here -> {context}")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        logger.info(f"in function generate_recommendations after executing the llm")
        print(response)
        logger.info(f"the recommnedations are {response}")
        recommendations = json.loads(response)

        return {"recommendations": recommendations}
    
    def assess_risk(self, state: Dict):
        """Assess the overall risk of the recommendations"""
        recommendations = state["recommendations"]
        
        prompt = f"""
        Analyze these investment recommendations and provide:
        1. An overall risk assessment (low, medium, high)
        2. A confidence score (0-1) for how well these match the client's profile
        3. Any potential concerns or red flags
        
        Recommendations:
        {json.dumps(recommendations, indent=2)}
        
        Return your analysis as JSON with keys: risk_assessment, confidence_score, concerns.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        risk_analysis = json.loads(response.content)
        return {"risk_analysis": risk_analysis}
    
    def finalize_output(self, state: Dict):
        """Combine all information into the final output"""
        client_id = state["client_id"]
        recommendations = state["recommendations"]
        risk_analysis = state["risk_analysis"]
        
        return InvestmentRecommendation(
            client_id=client_id,
            recommendations=recommendations,
            reasoning="Generated based on client profile and market context",
            risk_assessment=risk_analysis["risk_assessment"],
            confidence_score=risk_analysis["confidence_score"]
        )
    
    def generate_recommendation(self, client_id: int, client_data: Dict):
        """Execute the full recommendation workflow"""
        result = self.workflow.invoke({
            "client_id": client_id,
            "client_data": client_data
        })
        return result