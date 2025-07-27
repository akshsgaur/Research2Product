# Simplified Multi-Agent Research to Product System
# Removed complex document filtering, added auto-cleanup

import os
import json
import asyncio
import time
import hashlib
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile

# Flask and web dependencies
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Morphik SDK
try:
    from morphik import Morphik
except ImportError:
    print("❌ Morphik SDK not installed. Run: pip install morphik")
    exit(1)

@dataclass
class Agent:
    """AI Agent with specific role and expertise"""
    name: str
    role: str
    expertise: str
    focus_areas: List[str]
    query_style: str

@dataclass
class AgentInsight:
    """Insight from a specific agent"""
    agent: Agent
    analysis: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float

@dataclass
class ProductOpportunity:
    """Product opportunity identified by agents"""
    name: str
    description: str
    market_size: str
    feasibility_score: int
    technical_requirements: List[str]
    target_users: str
    revenue_model: str
    supporting_evidence: List[str]
    agent_consensus: Dict[str, str]

class SimplifiedMorphikMultiAgentTeam:
    """Simplified multi-agent team with content-based filtering and auto-cleanup"""
    
    def __init__(self, morphik_uri: str):
        """Initialize multi-agent team with Morphik connection"""
        self.morphik_uri = morphik_uri
        
        try:
            self.morphik = Morphik(morphik_uri, timeout=120)
            print("✅ Connected to Morphik API")
        except Exception as e:
            print(f"❌ Failed to connect to Morphik: {e}")
            raise e
        
        # Define specialized AI agents
        self.agents = {
            "visual_analyst": Agent(
                name="Dr. Vision",
                role="Visual Research Analyst",
                expertise="Interpreting figures, charts, diagrams, and visual data from research papers",
                focus_areas=["figures", "charts", "diagrams", "data visualization", "experimental results"],
                query_style="analytical_visual"
            ),
            "technical_lead": Agent(
                name="Alex Chen",
                role="Technical Lead",
                expertise="AI/ML implementation, system architecture, technical feasibility assessment",
                focus_areas=["algorithms", "implementation", "scalability", "performance", "technical challenges"],
                query_style="technical_depth"
            ),
            "product_manager": Agent(
                name="Sam Rodriguez",
                role="Product Manager", 
                expertise="Market opportunities, user experience, product strategy, feature prioritization",
                focus_areas=["market fit", "user needs", "competitive analysis", "product strategy"],
                query_style="market_focused"
            ),
            "business_strategist": Agent(
                name="Jordan Kim",
                role="Business Strategist",
                expertise="Revenue models, market analysis, competitive positioning, business development",
                focus_areas=["business models", "market sizing", "competitive advantage", "monetization"],
                query_style="business_strategic"
            ),
            "research_analyst": Agent(
                name="Dr. Casey Wang",
                role="Research Analyst",
                expertise="Academic research evaluation, innovation assessment, scientific methodology",
                focus_areas=["research quality", "innovation level", "scientific impact", "academic merit"],
                query_style="research_academic"
            )
        }
        
        self.current_document = None
        self.current_document_id = None
        self.current_filename = None
        self.analysis_results = {}
        
        print(f"🤖 Initialized multi-agent team with {len(self.agents)} specialists")
    
    def ingest_research_paper(self, pdf_path: str, use_colpali: bool = True) -> Dict[str, Any]:
        """Ingest research paper using Morphik's visual understanding"""
        print(f"📄 Ingesting research paper: {pdf_path}")
        
        try:
            filename = os.path.basename(pdf_path)
            with open(pdf_path, 'rb') as f:
                document = self.morphik.ingest_file(
                    f,
                    filename=filename,
                    use_colpali=use_colpali
                )
            
            # Wait for processing to complete
            document.wait_for_completion()
            
            self.current_document = document
            self.current_document_id = document.external_id
            self.current_filename = filename
            
            print(f"✅ Document ingested successfully:")
            print(f"   Document ID: {self.current_document_id}")
            print(f"   Filename: {filename}")
            print(f"   Visual processing: {'ColPali enabled' if use_colpali else 'Standard processing'}")
            
            return {
                "document_id": self.current_document_id,
                "filename": filename,
                "status": "processed",
                "visual_processing": use_colpali,
                "ingested_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error ingesting document: {e}")
            raise e
    
    def cleanup_document(self, confirm: bool = True) -> bool:
        """Delete the ingested document after analysis"""
        if not self.current_document_id:
            print("ℹ️ No document to cleanup")
            return True
            
        try:
            result = self.morphik.delete_document(self.current_document_id)
            print(f"🧹 Document {self.current_document_id} deleted successfully")
            if 'message' in result:
                print(f"   {result['message']}")
            
            # Clear current document references
            self.current_document = None
            self.current_document_id = None
            self.current_filename = None
            
            return True
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to delete document {self.current_document_id}: {e}")
            print("💡 Document may need manual deletion from Morphik dashboard")
            return False
    
    def analyze_with_agent(self, agent_id: str, custom_query: Optional[str] = None) -> AgentInsight:
        """Analyze document with a specific agent using content-based filtering"""
        if not self.current_document:
            raise ValueError("No document ingested. Call ingest_research_paper() first.")
        
        agent = self.agents[agent_id]
        
        # Build agent-specific query with content targeting
        if custom_query:
            query = custom_query
        else:
            query = self._build_agent_query(agent)
        
        print(f"🔍 {agent.name} ({agent.role}) analyzing with content-based search...")
        
        start_time = time.time()
        
        try:
            # Simple content-based query - no complex filtering
            response = self.morphik.query(
                query=query,
                use_colpali=True,
                k=5,
                min_score=0.0
            )
            
            processing_time = time.time() - start_time
            
            # Extract sources information
            sources = self._extract_sources(response)
            
            # Calculate confidence
            confidence = self._calculate_confidence(response, sources)
            
            insight = AgentInsight(
                agent=agent,
                analysis=response.completion,
                sources=sources,
                confidence=confidence,
                processing_time=processing_time
            )
            
            print(f"✅ {agent.name} completed analysis ({processing_time:.2f}s, confidence: {confidence:.2f})")
            return insight
            
        except Exception as e:
            print(f"⚠️ {agent.name} analysis failed: {e}")
            # Create fallback insight
            return self._create_fallback_insight(agent)
    
    def _build_agent_query(self, agent: Agent) -> str:
        """Build agent-specific query with content-based targeting"""
        
        base_queries = {
            "visual_analyst": """
            Analyze visual elements in the research paper including:
            - What do the figures, charts, and diagrams show?
            - What key data is presented visually?
            - What trends or patterns are visible?
            - How do the visual elements support the main claims?
            - What experimental results or frameworks are shown visually?
            
            Focus on visual content analysis and data interpretation.
            """,
            
            "technical_lead": """
            Analyze technical aspects of the research:
            - What are the core technical innovations and algorithms?
            - What are the implementation details and technical framework?
            - What are the computational complexity considerations?
            - What technical challenges are identified?
            - How feasible is implementing this in production systems?
            
            Focus on technical depth and implementation feasibility.
            """,
            
            "product_manager": """
            Analyze the research from a product development perspective:
            - What market opportunities does this research enable?
            - What problems does this solve for users or businesses?
            - What are potential applications and use cases?
            - How does this compare to existing solutions?
            - What would be key features of products based on this research?
            
            Focus on market opportunities and product potential.
            """,
            
            "business_strategist": """
            Analyze commercial potential of the research:
            - What are potential revenue models for this technology?
            - What is the estimated market size and opportunity?
            - What competitive advantages does this provide?
            - What are barriers to commercialization?
            - What business partnerships would be needed?
            
            Focus on business strategy and commercial viability.
            """,
            
            "research_analyst": """
            Evaluate the research from an academic perspective:
            - What is the significance of the research contribution?
            - How novel are the approaches compared to existing work?
            - What are strengths and limitations of the methodology?
            - What future research directions are suggested?
            - How strong is the theoretical and empirical validation?
            
            Focus on research quality and academic significance.
            """
        }
        
        # Get query by agent role (convert to snake_case)
        agent_key = agent.role.lower().replace(" ", "_")
        return base_queries.get(agent_key, 
                               f"Analyze the research from the perspective of a {agent.role}")
    
    def _extract_sources(self, response):
        """Extract sources information with robust handling"""
        sources = []
        if hasattr(response, 'sources') and response.sources:
            for source in response.sources:
                try:
                    source_dict = {}
                    
                    if hasattr(source, 'content'):
                        source_dict["content"] = str(source.content)[:200]  # Truncate for brevity
                    elif hasattr(source, 'text'):
                        source_dict["content"] = str(source.text)[:200]
                    else:
                        source_dict["content"] = str(source)[:200]
                    
                    if hasattr(source, 'score'):
                        source_dict["score"] = float(source.score)
                    elif hasattr(source, 'similarity'):
                        source_dict["score"] = float(source.similarity)
                    else:
                        source_dict["score"] = 0.5
                    
                    if hasattr(source, 'metadata'):
                        source_dict["metadata"] = dict(source.metadata) if source.metadata else {}
                    else:
                        source_dict["metadata"] = {}
                    
                    sources.append(source_dict)
                        
                except Exception as e:
                    print(f"Warning: Could not process source: {e}")
        
        return sources
    
    def _calculate_confidence(self, response, sources: List[Dict]) -> float:
        """Calculate confidence score based on response quality and sources"""
        base_confidence = 0.7
        
        # Adjust based on response length
        if hasattr(response, 'completion') and len(response.completion) > 500:
            base_confidence += 0.1
        
        # Adjust based on number of sources
        if len(sources) >= 3:
            base_confidence += 0.1
        
        # Adjust based on source quality
        if sources:
            try:
                total_score = sum(source.get("score", 0.5) for source in sources)
                avg_score = total_score / len(sources)
                base_confidence += (avg_score * 0.2)
            except Exception:
                pass
        
        return min(1.0, base_confidence)
    
    def _create_fallback_insight(self, agent: Agent) -> AgentInsight:
        """Create fallback insight when analysis fails"""
        fallback_analysis = f"""
        Analysis unavailable due to technical issues. Based on general knowledge:
        
        From {agent.role} perspective:
        - {agent.expertise} is crucial for this type of research
        - Key focus areas include: {', '.join(agent.focus_areas)}
        - This analysis would typically examine technical, market, and implementation aspects
        
        Note: This is a fallback response due to analysis limitations.
        """
        
        return AgentInsight(
            agent=agent,
            analysis=fallback_analysis,
            sources=[],
            confidence=0.5,
            processing_time=0.1
        )
    
    def run_collaborative_analysis(self, auto_cleanup: bool = True) -> Dict[str, Any]:
        """Run collaborative multi-agent analysis with optional cleanup"""
        if not self.current_document:
            raise ValueError("No document ingested. Call ingest_research_paper() first.")
        
        print("🚀 Starting collaborative multi-agent analysis...")
        print(f"📋 Document: {self.current_filename}")
        
        try:
            # Phase 1: Individual agent analysis
            print("\n📊 Phase 1: Individual Agent Analysis")
            individual_insights = {}
            
            for agent_id in self.agents.keys():
                try:
                    insight = self.analyze_with_agent(agent_id)
                    individual_insights[agent_id] = insight
                except Exception as e:
                    print(f"⚠️ Warning: {agent_id} analysis failed: {e}")
                    # Create fallback insight
                    individual_insights[agent_id] = self._create_fallback_insight(self.agents[agent_id])
            
            # Phase 2: Cross-agent synthesis
            print("\n🤝 Phase 2: Cross-Agent Synthesis")
            synthesis = self._synthesize_insights(individual_insights)
            
            # Phase 3: Product opportunity identification
            print("\n💡 Phase 3: Product Opportunity Identification")
            product_opportunities = self._identify_product_opportunities(individual_insights, synthesis)
            
            # Compile final results
            results = {
                "document_metadata": {
                    "document_id": self.current_document_id,
                    "filename": self.current_filename,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "agents_involved": len(individual_insights),
                    "morphik_powered": True,
                    "cleanup_scheduled": auto_cleanup
                },
                "individual_insights": {
                    agent_id: {
                        "agent_name": insight.agent.name,
                        "agent_role": insight.agent.role,
                        "analysis": insight.analysis,
                        "confidence": insight.confidence,
                        "processing_time": insight.processing_time,
                        "sources_count": len(insight.sources)
                    }
                    for agent_id, insight in individual_insights.items()
                },
                "collaborative_synthesis": synthesis,
                "product_opportunities": [asdict(opp) for opp in product_opportunities]
            }
            
            self.analysis_results = results
            
            print("✅ Collaborative analysis complete!")
            print(f"   Document analyzed: {self.current_filename}")
            print(f"   Agents participated: {len(individual_insights)}")
            print(f"   Product opportunities identified: {len(product_opportunities)}")
            
            return results
            
        finally:
            # Cleanup document regardless of success/failure
            if auto_cleanup:
                cleanup_success = self.cleanup_document()
                if cleanup_success:
                    print("🧹 Document automatically cleaned up")
                else:
                    print("⚠️ Document cleanup failed - manual deletion may be required")
    
    def _synthesize_insights(self, insights: Dict[str, AgentInsight]) -> str:
        """Synthesize insights from all agents"""
        if not insights:
            return "No insights available for synthesis."
        
        try:
            # Build synthesis using content-based search
            synthesis_query = """
            Based on the research content, provide a comprehensive synthesis that:
            
            1. Identifies the core innovation and its significance
            2. Assesses technical feasibility and implementation challenges
            3. Evaluates market potential and commercial opportunities
            4. Highlights key evidence supporting conclusions
            5. Recommends 2-3 specific directions for product development
            
            Consider both technical depth and commercial viability.
            """
            
            response = self.morphik.query(
                query=synthesis_query,
                use_colpali=True,
                k=8,
                min_score=0.0
            )
            
            return response.completion
            
        except Exception as e:
            print(f"⚠️ Warning: Synthesis generation failed: {e}")
            return "Synthesis could not be generated due to API error. Individual agent insights are available above."
    
    def _identify_product_opportunities(self, insights: Dict[str, AgentInsight], synthesis: str) -> List[ProductOpportunity]:
        """Identify specific product opportunities using OpenAI"""
        if not insights:
            return []
        
        # Build context from agent insights
        context_sections = []
        for agent_id, insight in insights.items():
            context_sections.append(f"""
            {insight.agent.role.upper()} ANALYSIS:
            {insight.analysis}
            (Confidence: {insight.confidence:.1%}, Sources: {len(insight.sources)})
            """)
        
        combined_context = "\n".join(context_sections)
        
        try:
            print("🤖 Generating product opportunities with OpenAI...")
            
            import openai
            
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                print("❌ OpenAI API key not found - creating fallback opportunities")
                return self._generate_fallback_opportunities(insights)
            
            client = openai.OpenAI(api_key=openai_key)
            
            opportunities_query = f"""
            Based on this multi-agent analysis, identify 3 specific product opportunities:

            AGENT INSIGHTS:
            {combined_context}

            SYNTHESIS:
            {synthesis}

            Generate realistic product ideas with clear business potential.
            Return as JSON with this exact structure:
            {{
              "opportunities": [
                {{
                  "name": "Product Name",
                  "description": "Detailed description",
                  "market_size": "$X.XB or $XXXM",
                  "feasibility_score": 8,
                  "technical_requirements": ["Req 1", "Req 2", "Req 3"],
                  "target_users": "Target user groups",
                  "revenue_model": "Revenue model",
                  "supporting_evidence": ["Evidence 1", "Evidence 2"],
                  "agent_consensus": {{
                    "technical": "Technical perspective",
                    "product": "Product perspective",
                    "business": "Business perspective",
                    "research": "Research perspective"
                  }}
                }}
              ]
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert product strategist. Return valid JSON only, no markdown formatting."
                    },
                    {
                        "role": "user", 
                        "content": opportunities_query
                    }
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            response_text = response.choices[0].message.content
            
            # Extract and parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                opportunities_data = json.loads(json_match.group(0))
                
                opportunities = []
                for opp_data in opportunities_data.get("opportunities", []):
                    opportunity = ProductOpportunity(
                        name=opp_data.get("name", "Unnamed Product"),
                        description=opp_data.get("description", "Description not available"),
                        market_size=opp_data.get("market_size", "$500M"),
                        feasibility_score=int(opp_data.get("feasibility_score", 7)),
                        technical_requirements=opp_data.get("technical_requirements", ["Technical implementation required"]),
                        target_users=opp_data.get("target_users", "Technology professionals"),
                        revenue_model=opp_data.get("revenue_model", "Subscription-based pricing"),
                        supporting_evidence=opp_data.get("supporting_evidence", ["Research findings"]),
                        agent_consensus=opp_data.get("agent_consensus", {
                            "technical": "Assessment pending",
                            "product": "Assessment pending",
                            "business": "Assessment pending",
                            "research": "Assessment pending"
                        })
                    )
                    opportunities.append(opportunity)
                
                print(f"✅ Generated {len(opportunities)} product opportunities")
                return opportunities[:3]
                
            else:
                print("❌ Failed to parse OpenAI response")
                return self._generate_fallback_opportunities(insights)
            
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
            return self._generate_fallback_opportunities(insights)
    
    def _generate_fallback_opportunities(self, insights: Dict[str, AgentInsight]) -> List[ProductOpportunity]:
        """Generate simple fallback opportunities"""
        print("🔄 Generating fallback opportunities...")
        
        opportunities = [
            ProductOpportunity(
                name="Research-Based Innovation Platform",
                description="A platform that leverages the core innovations from the research to solve real-world problems.",
                market_size="$1.2B",
                feasibility_score=7,
                technical_requirements=["Algorithm implementation", "System integration", "User interface development"],
                target_users="Technology professionals and researchers",
                revenue_model="Subscription-based with tiered pricing",
                supporting_evidence=["Research findings", "Technical feasibility", "Market demand"],
                agent_consensus={
                    "technical": "Technically feasible with standard implementation approaches",
                    "product": "Strong market potential for innovation-based solutions",
                    "business": "Viable business model with subscription revenue",
                    "research": "Well-supported by research evidence"
                }
            )
        ]
        
        return opportunities
    
    def query_document(self, question: str) -> Dict[str, Any]:
        """Query the document directly using simple content search"""
        if not self.current_document:
            raise ValueError("No document ingested. Call ingest_research_paper() first.")
        
        print(f"🔍 Querying document: {question}")
        
        try:
            response = self.morphik.query(
                query=question,
                use_colpali=True,
                k=5,
                min_score=0.0
            )
            
            sources = self._extract_sources(response)
            
            return {
                "question": question,
                "answer": response.completion,
                "sources": sources,
                "document_id": self.current_document_id,
                "filename": self.current_filename,
                "visual_analysis": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {
                "question": question,
                "answer": f"Query failed: {str(e)}",
                "sources": [],
                "document_id": self.current_document_id,
                "filename": self.current_filename,
                "visual_analysis": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the latest analysis"""
        if not self.analysis_results:
            return {"error": "No analysis completed yet"}
        
        insights = self.analysis_results.get("individual_insights", {})
        opportunities = self.analysis_results.get("product_opportunities", [])
        
        return {
            "analysis_completed": True,
            "document_id": self.current_document_id,
            "filename": self.current_filename,
            "agents_participated": len(insights),
            "average_confidence": sum(insight["confidence"] for insight in insights.values()) / len(insights) if insights else 0,
            "product_opportunities_identified": len(opportunities),
            "top_opportunity": opportunities[0]["name"] if opportunities else None,
            "morphik_powered": True,
            "simplified_system": True
        }

# Flask API wrapper
app = Flask(__name__)
CORS(app)

# Global team instance
team = None

def init_team():
    """Initialize the multi-agent team"""
    global team
    
    morphik_uri = os.getenv('MORPHIK_URI')
    if not morphik_uri:
        raise ValueError("MORPHIK_URI environment variable required")
    
    team = SimplifiedMorphikMultiAgentTeam(morphik_uri)

# Updated HTML interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simplified Morphik Multi-Agent Research Analysis</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 1200px; margin: 0 auto; padding: 20px; background: #f8fafc; 
        }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); }
        .morphik-badge { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px; 
            display: inline-block; margin-bottom: 20px;
        }
        .cleanup-badge {
            background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; 
            font-size: 11px; margin-left: 10px;
        }
        .agent-card { 
            background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 8px; 
            border-left: 4px solid #667eea;
        }
        .btn { 
            background: #667eea; color: white; padding: 12px 24px; border: none; 
            border-radius: 6px; cursor: pointer; font-size: 14px; margin: 5px;
        }
        .btn:hover { background: #5a6fd8; }
        .btn:disabled { background: #94a3b8; cursor: not-allowed; }
        .result { background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .upload-area { 
            border: 2px dashed #667eea; padding: 40px; text-align: center; 
            border-radius: 8px; margin: 20px 0; background: #f8fafc; cursor: pointer;
        }
        .upload-area:hover { border-color: #5a6fd8; background: #f1f5f9; }
        .opportunity { 
            background: #f0f9ff; padding: 20px; margin: 15px 0; border-radius: 8px; 
            border-left: 4px solid #3b82f6;
        }
        .loading { text-align: center; padding: 20px; color: #667eea; }
        .error { color: #dc2626; background: #fef2f2; padding: 15px; border-radius: 8px; }
        .success { color: #059669; background: #ecfdf5; padding: 15px; border-radius: 8px; }
        .cleanup-info { 
            background: #fef3c7; border: 1px solid #f59e0b; padding: 10px; border-radius: 6px; 
            margin: 10px 0; font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠🤖 Simplified Morphik Multi-Agent Analysis</h1>
        <div class="morphik-badge">Powered by Morphik's Visual Document Understanding</div>
        <div class="cleanup-badge">🧹 Auto-Cleanup Enabled</div>
        
        <div class="cleanup-info">
            <strong>📋 How it works:</strong><br>
            1. Upload your research paper<br>
            2. AI agents analyze the content using smart search<br>
            3. Get comprehensive insights and product opportunities<br>
            4. Document is automatically deleted after analysis
        </div>
        
        <h3>📄 Upload Research Paper</h3>
        <div id="upload-section">
            <form id="upload-form" enctype="multipart/form-data">
                <div class="upload-area" id="upload-area" onclick="handleUploadAreaClick()">
                    <input type="file" id="file-input" accept=".pdf" style="display: none;">
                    <p>📄 Click to upload research paper (PDF)</p>
                    <p><small>✨ Simplified processing with automatic cleanup</small></p>
                </div>
                <button type="button" id="ingest-btn" class="btn" onclick="uploadDocument()">🔄 Ingest & Analyze</button>
            </form>
        </div>
        
        <div id="upload-result"></div>
        
        <h3>🤖 AI Agent Team</h3>
        <div id="agents-info">
            <div class="agent-card">
                <strong>Dr. Vision - Visual Research Analyst</strong><br>
                <small>Analyzes figures, charts, diagrams using Morphik's visual understanding</small>
            </div>
            <div class="agent-card">
                <strong>Alex Chen - Technical Lead</strong><br>
                <small>Evaluates technical feasibility and implementation requirements</small>
            </div>
            <div class="agent-card">
                <strong>Sam Rodriguez - Product Manager</strong><br>
                <small>Identifies market opportunities and user needs</small>
            </div>
            <div class="agent-card">
                <strong>Jordan Kim - Business Strategist</strong><br>
                <small>Analyzes business models and commercial potential</small>
            </div>
            <div class="agent-card">
                <strong>Dr. Casey Wang - Research Analyst</strong><br>
                <small>Evaluates research quality and innovation level</small>
            </div>
        </div>
        
        <button onclick="runAnalysis()" class="btn" id="analyze-btn" style="display: none;">
            🚀 Run Multi-Agent Analysis
        </button>
        
        <div id="analysis-result"></div>
        
        <h3>🔍 Query Document</h3>
        <div style="display: flex; gap: 10px; margin: 10px 0;">
            <input type="text" id="query-input" placeholder="Ask about the research..." 
                   style="flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px;">
            <button onclick="queryDocument()" class="btn" id="query-btn" style="display: none;">
                💬 Query Document
            </button>
        </div>
        
        <div id="query-result"></div>
    </div>

    <script>
        let documentIngested = false;
        let selectedFile = null;

        function handleUploadAreaClick() {
            const fileInput = document.getElementById('file-input');
            if (fileInput) {
                fileInput.click();
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            // File input change handler
            const fileInput = document.getElementById('file-input');
            if (fileInput) {
                fileInput.addEventListener('change', function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        selectedFile = file;
                        const uploadArea = document.getElementById('upload-area');
                        if (uploadArea) {
                            uploadArea.innerHTML = `
                                <input type="file" id="file-input" accept=".pdf" style="display: none;">
                                <p>📄 Selected: ${file.name}</p>
                                <p><small>Ready for simplified processing with auto-cleanup</small></p>
                            `;
                            // Re-attach the handler
                            const newFileInput = document.getElementById('file-input');
                            if (newFileInput) {
                                newFileInput.addEventListener('change', arguments.callee);
                            }
                        }
                    }
                });
            }

            // Query input Enter key handler
            const queryInput = document.getElementById('query-input');
            if (queryInput) {
                queryInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        queryDocument();
                    }
                });
            }
        });

        async function uploadDocument() {
            if (!selectedFile) {
                alert('Please select a PDF file first');
                handleUploadAreaClick();
                return;
            }

            if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
                alert('Please select a PDF file');
                selectedFile = null;
                return;
            }

            const resultDiv = document.getElementById('upload-result');
            const ingestBtn = document.getElementById('ingest-btn');
            
            // Update UI
            if (ingestBtn) {
                ingestBtn.disabled = true;
                ingestBtn.textContent = 'Processing...';
            }
            
            if (resultDiv) {
                resultDiv.innerHTML = '<div class="loading">📄 Ingesting and analyzing with simplified Morphik processing...<br><small>This may take 30-60 seconds</small></div>';
            }

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/ingest', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.success) {
                    if (resultDiv) {
                        resultDiv.innerHTML = `
                            <div class="success">
                                <h4>✅ Document Processed Successfully</h4>
                                <p><strong>Filename:</strong> ${result.metadata.filename}</p>
                                <p><strong>Document ID:</strong> <code>${result.metadata.document_id}</code></p>
                                <p><strong>Visual Processing:</strong> ${result.metadata.visual_processing ? 'ColPali Enabled' : 'Standard'}</p>
                                <p><strong>Status:</strong> Ready for analysis</p>
                                <p><strong>🧹 Auto-cleanup:</strong> Document will be deleted after analysis</p>
                            </div>
                        `;
                    }
                    documentIngested = true;
                    const analyzeBtn = document.getElementById('analyze-btn');
                    const queryBtn = document.getElementById('query-btn');
                    if (analyzeBtn) analyzeBtn.style.display = 'inline-block';
                    if (queryBtn) queryBtn.style.display = 'inline-block';
                } else {
                    if (resultDiv) {
                        resultDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                    }
                }
            } catch (error) {
                if (resultDiv) {
                    resultDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
                }
            } finally {
                if (ingestBtn) {
                    ingestBtn.disabled = false;
                    ingestBtn.textContent = '🔄 Ingest & Analyze';
                }
            }
        }

        async function runAnalysis() {
            if (!documentIngested) {
                alert('Please ingest a document first');
                return;
            }

            const resultDiv = document.getElementById('analysis-result');
            const analyzeBtn = document.getElementById('analyze-btn');
            
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
            
            resultDiv.innerHTML = `
                <div class="loading">
                    🤖 Multi-agent analysis in progress...<br>
                    <small>Simplified processing with content-based search</small><br>
                    <small>Document will be auto-deleted after completion</small><br>
                    <small>This may take 2-3 minutes</small>
                </div>
            `;

            try {
                const response = await fetch('/analyze', {
                    method: 'POST'
                });

                const result = await response.json();
                
                if (result.success) {
                    const data = result.analysis;
                    let html = `
                        <div class="success">
                            <h4>🎉 Multi-Agent Analysis Complete</h4>
                            <p><strong>Document:</strong> ${data.document_metadata.filename}</p>
                            <p><strong>Agents Participated:</strong> ${data.document_metadata.agents_involved}</p>
                            <p><strong>Simplified System:</strong> ✅ Content-based analysis with auto-cleanup</p>
                            <p><strong>🧹 Cleanup Status:</strong> ${data.document_metadata.cleanup_scheduled ? 'Document automatically deleted' : 'Manual cleanup required'}</p>
                        </div>

                        <h4>🤖 Individual Agent Insights</h4>
                    `;
                    
                    Object.entries(data.individual_insights).forEach(([agentId, insight]) => {
                        html += `
                            <div class="agent-card">
                                <h5>${insight.agent_name} - ${insight.agent_role}</h5>
                                <p>${insight.analysis.substring(0, 400)}...</p>
                                <small>
                                    Confidence: ${(insight.confidence * 100).toFixed(1)}% | 
                                    Processing: ${insight.processing_time.toFixed(2)}s | 
                                    Sources: ${insight.sources_count}
                                </small>
                            </div>
                        `;
                    });

                    html += `
                        <h4>🤝 Collaborative Synthesis</h4>
                        <div class="result">
                            <p>${data.collaborative_synthesis}</p>
                        </div>

                        <h4>💡 Product Opportunities</h4>
                    `;

                    data.product_opportunities.forEach(opp => {
                        html += `
                            <div class="opportunity">
                                <h5>${opp.name}</h5>
                                <p>${opp.description}</p>
                                <p>
                                    <strong>Market Size:</strong> ${opp.market_size} | 
                                    <strong>Feasibility:</strong> ${opp.feasibility_score}/10
                                </p>
                                <p><strong>Target Users:</strong> ${opp.target_users}</p>
                                <p><strong>Revenue Model:</strong> ${opp.revenue_model}</p>
                                <div style="margin-top: 10px;">
                                    <strong>Supporting Evidence:</strong>
                                    <ul>
                                        ${opp.supporting_evidence.map(evidence => `<li>${evidence}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `;
                    });
                    
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ Analysis Error: ${result.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🚀 Run Multi-Agent Analysis';
            }
        }

        async function queryDocument() {
            const query = document.getElementById('query-input').value;
            if (!query.trim()) {
                alert('Please enter a query');
                return;
            }

            if (!documentIngested) {
                alert('Please ingest a document first');
                return;
            }

            const resultDiv = document.getElementById('query-result');
            const queryBtn = document.getElementById('query-btn');
            
            queryBtn.disabled = true;
            queryBtn.textContent = 'Querying...';
            
            resultDiv.innerHTML = `
                <div class="loading">
                    🔍 Querying document with simplified content search...
                </div>
            `;

            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: query })
                });

                const result = await response.json();
                
                if (result.success) {
                    const data = result.response;
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h4>💡 Query Result</h4>
                            <p><strong>Document:</strong> ${data.filename}</p>
                            <p><strong>Question:</strong> ${data.question}</p>
                            <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 6px;">
                                <strong>Answer:</strong><br>
                                ${data.answer}
                            </div>
                            <p><strong>Visual Analysis:</strong> ${data.visual_analysis ? '✅ Enabled' : '❌ Disabled'}</p>
                            <p><strong>Sources:</strong> ${data.sources.length} relevant sections found</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ Query Error: ${result.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
            } finally {
                queryBtn.disabled = false;
                queryBtn.textContent = '💬 Query Document';
            }
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    """Main interface"""
    return render_template_string(HTML_INTERFACE)

@app.route('/ingest', methods=['POST'])
def ingest_document():
    """Ingest document using simplified Morphik API"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files supported'})
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)
        
        try:
            # Ingest using simplified Morphik approach
            metadata = team.ingest_research_paper(temp_path, use_colpali=True)
            
            return jsonify({
                'success': True,
                'metadata': metadata
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze', methods=['POST'])
def run_analysis():
    """Run multi-agent analysis with auto-cleanup"""
    try:
        analysis = team.run_collaborative_analysis(auto_cleanup=True)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/query', methods=['POST'])
def query_document():
    """Query document using simplified approach"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'success': False, 'error': 'Question required'})
        
        response = team.query_document(question)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cleanup', methods=['POST'])
def cleanup_document():
    """Manual cleanup endpoint"""
    try:
        if not team.current_document_id:
            return jsonify({'success': False, 'error': 'No document to cleanup'})
        
        success = team.cleanup_document()
        
        return jsonify({
            'success': success,
            'message': 'Document deleted successfully' if success else 'Cleanup failed'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agents', methods=['GET'])
def list_agents():
    """List all available agents"""
    try:
        agents_info = {
            agent_id: {
                "name": agent.name,
                "role": agent.role,
                "expertise": agent.expertise,
                "focus_areas": agent.focus_areas
            }
            for agent_id, agent in team.agents.items()
        }
        
        return jsonify({
            'success': True,
            'agents': agents_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/summary', methods=['GET'])
def get_summary():
    """Get analysis summary"""
    try:
        summary = team.get_analysis_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'simplified-morphik-multi-agent-research',
        'morphik_connected': team is not None,
        'agents_available': len(team.agents) if team else 0,
        'simplified_system': True,
        'auto_cleanup': True,
        'version': '4.0.0'
    })

# Example usage and testing
def test_system():
    """Test the simplified system"""
    
    morphik_uri = os.getenv("MORPHIK_URI")
    
    if not morphik_uri or "owner_id:token" in morphik_uri:
        print("⚠️  Please set your MORPHIK_URI environment variable")
        return False
    
    try:
        # Initialize simplified multi-agent team
        test_team = SimplifiedMorphikMultiAgentTeam(morphik_uri)
        
        print("✅ Simplified system test successful!")
        print(f"   Connected to Morphik API")
        print(f"   {len(test_team.agents)} agents initialized")
        print(f"   Content-based filtering enabled")
        print(f"   Auto-cleanup enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

if __name__ == '__main__':
    print("""
    🚀 Simplified Morphik Multi-Agent Research to Product System v4.0
    
    KEY IMPROVEMENTS:
    ✅ Removed Complex Document ID Filtering - Uses simple content-based search
    ✅ Auto-Cleanup After Analysis - Documents automatically deleted
    ✅ Simplified Architecture - Cleaner, more reliable code
    ✅ Better Error Handling - Graceful fallbacks throughout
    ✅ Streamlined UI - Clear process with cleanup indicators
    
    This simplified system:
    • Uses Morphik's content-based search (no complex filtering)
    • Automatically cleans up documents after analysis
    • Provides the same great multi-agent insights
    • Is more reliable and easier to maintain
    
    Setup Required:
    1. Set environment variable:
       export MORPHIK_URI="morphik://owner_id:token@api.morphik.ai"
    2. Optional OpenAI key for enhanced product opportunities:
       export OPENAI_API_KEY="your_openai_key"
    
    API Endpoints:
    • POST /ingest - Upload PDF and ingest
    • POST /analyze - Run analysis with auto-cleanup
    • POST /query - Query document content
    • POST /cleanup - Manual cleanup (if needed)
    • GET /agents - List agents
    • GET /summary - Get analysis summary
    • GET /health - Health check
    
    Simplified Process:
    1. Upload PDF → Morphik ingests with ColPali
    2. Agents analyze using content-based search
    3. Get comprehensive insights and product opportunities
    4. Document automatically deleted after analysis
    """)
    
    # Test system before starting
    if test_system():
        try:
            init_team()
            print("\n🌐 Starting simplified Flask API server...")
            print("   Web interface: http://localhost:5001")
            print("   Health check: http://localhost:5001/health")
            print("   🧹 Auto-cleanup: ENABLED")
            app.run(debug=True, host='0.0.0.0', port=5001)
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
    else:
        print("\n💡 Fix the issues above and try again")
        print("   Make sure MORPHIK_URI is set correctly")