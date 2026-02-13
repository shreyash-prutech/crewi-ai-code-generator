import os
from typing import Dict, List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    requirement: str = Field(
        ...,
        description="The software requirement or feature request to research"
    )
    project_context: Optional[str] = Field(
        default=None,
        description="Additional project context or existing codebase information"
    )


class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research on software requirements following a structured process: "
        "gathers relevant context and memories, analyzes and reasons iteratively, "
        "identifies gaps and assumptions, and synthesizes findings into a comprehensive "
        "Markdown research plan with problem analysis, technical approach, design decisions, "
        "trade-offs, risks, and implementation roadmap."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput
    
    def _run(self, requirement: str, project_context: Optional[str] = None) -> str:
        try:
            context = self._gather_context(requirement, project_context)
            analysis = self._analyze_and_reason(context)
            gaps = self._identify_gaps(analysis)
            findings = self._synthesize_findings(context, analysis, gaps)
            
            return self._generate_markdown_plan(findings)
            
        except Exception as e:
            return f"Error during deep research: {str(e)}"
    
    def _gather_context(self, requirement: str, project_context: Optional[str]) -> Dict:
        context = {
            "requirement": requirement,
            "project_context": project_context or "",
            "key_features": [],
            "technologies": [],
            "constraints": [],
            "stakeholders": [],
            "domain": ""
        }
        
        req_lower = requirement.lower()
        
        if any(word in req_lower for word in ["web", "website", "frontend", "ui", "react", "vue", "angular"]):
            context["technologies"].extend(["Frontend Framework", "HTML/CSS", "JavaScript"])
        
        if any(word in req_lower for word in ["api", "backend", "server", "database", "rest", "graphql"]):
            context["technologies"].extend(["Backend Framework", "Database", "API"])
        
        if any(word in req_lower for word in ["mobile", "app", "ios", "android", "react native", "flutter"]):
            context["technologies"].extend(["Mobile Framework", "Cross-platform"])
        
        if any(word in req_lower for word in ["real-time", "chat", "messaging", "websocket"]):
            context["technologies"].extend(["WebSocket", "Real-time Communication"])
        
        if any(word in req_lower for word in ["auth", "login", "user", "account", "security"]):
            context["key_features"].extend(["Authentication", "User Management", "Security"])
        
        if any(word in req_lower for word in ["payment", "billing", "subscription", "checkout"]):
            context["key_features"].extend(["Payment Processing", "Billing System"])
        
        if any(word in req_lower for word in ["analytics", "dashboard", "reporting", "metrics"]):
            context["key_features"].extend(["Analytics", "Reporting", "Dashboard"])
        
        if any(word in req_lower for word in ["e-commerce", "shop", "store", "product", "cart"]):
            context["domain"] = "E-commerce"
        elif any(word in req_lower for word in ["social", "community", "network", "feed"]):
            context["domain"] = "Social Platform"
        elif any(word in req_lower for word in ["finance", "banking", "investment", "trading"]):
            context["domain"] = "Financial Services"
        elif any(word in req_lower for word in ["health", "medical", "patient", "doctor"]):
            context["domain"] = "Healthcare"
        elif any(word in req_lower for word in ["education", "learning", "course", "student"]):
            context["domain"] = "Education"
        else:
            context["domain"] = "General Business Application"
        
        context["stakeholders"] = ["End Users", "Administrators", "Developers", "Business Stakeholders"]
        
        if "performance" in req_lower or "scale" in req_lower:
            context["constraints"].append("High Performance Requirements")
        if "secure" in req_lower or "privacy" in req_lower:
            context["constraints"].append("Security and Privacy Compliance")
        if "mobile" in req_lower:
            context["constraints"].append("Mobile Responsiveness")
        
        return context
    
    def _analyze_and_reason(self, context: Dict) -> Dict:
        analysis = {
            "technical_complexity": "Medium",
            "architecture_pattern": "",
            "data_flow": [],
            "integration_points": [],
            "scalability_considerations": [],
            "security_requirements": [],
            "performance_requirements": []
        }
        
        tech_count = len(context["technologies"])
        feature_count = len(context["key_features"])
        
        if tech_count >= 4 or feature_count >= 4:
            analysis["technical_complexity"] = "High"
        elif tech_count <= 2 and feature_count <= 2:
            analysis["technical_complexity"] = "Low"
        
        if "Frontend Framework" in context["technologies"] and "Backend Framework" in context["technologies"]:
            analysis["architecture_pattern"] = "Client-Server Architecture with API Layer"
            analysis["data_flow"] = ["Client Request", "API Gateway", "Business Logic", "Database", "Response"]
        elif "Mobile Framework" in context["technologies"]:
            analysis["architecture_pattern"] = "Mobile-First Architecture"
            analysis["data_flow"] = ["Mobile App", "API Layer", "Backend Services", "Data Storage"]
        else:
            analysis["architecture_pattern"] = "Monolithic Architecture"
            analysis["data_flow"] = ["User Interface", "Application Logic", "Data Layer"]
        
        if "Real-time Communication" in context["technologies"]:
            analysis["integration_points"].append("WebSocket Server")
        if "Payment Processing" in context["key_features"]:
            analysis["integration_points"].append("Payment Gateway API")
        if "Analytics" in context["key_features"]:
            analysis["integration_points"].append("Analytics Service")
        
        if context["domain"] in ["E-commerce", "Social Platform", "Financial Services"]:
            analysis["scalability_considerations"] = [
                "Horizontal scaling capability",
                "Database optimization",
                "Caching strategy",
                "Load balancing"
            ]
        
        if "Security and Privacy Compliance" in context["constraints"] or context["domain"] == "Financial Services":
            analysis["security_requirements"] = [
                "Data encryption at rest and in transit",
                "Authentication and authorization",
                "Input validation and sanitization",
                "Security audit logging"
            ]
        
        if "High Performance Requirements" in context["constraints"]:
            analysis["performance_requirements"] = [
                "Response time optimization",
                "Database query optimization",
                "Caching implementation",
                "CDN integration"
            ]
        
        return analysis
    
    def _identify_gaps(self, analysis: Dict) -> Dict:
        gaps = {
            "missing_requirements": [],
            "assumptions": [],
            "potential_issues": [],
            "unclear_aspects": []
        }
        
        if not analysis["security_requirements"]:
            gaps["missing_requirements"].append("Security requirements not clearly defined")
        
        if not analysis["performance_requirements"]:
            gaps["missing_requirements"].append("Performance criteria not specified")
        
        if not analysis["integration_points"]:
            gaps["assumptions"].append("Assuming minimal external integrations required")
        
        gaps["assumptions"].extend([
            "Standard web technologies will be sufficient",
            "Users have reliable internet connectivity",
            "Development team has expertise in chosen technologies"
        ])
        
        if analysis["technical_complexity"] == "High":
            gaps["potential_issues"].extend([
                "Complex system integration challenges",
                "Increased development time and cost",
                "Higher maintenance overhead"
            ])
        
        if analysis["scalability_considerations"]:
            gaps["potential_issues"].append("Scalability bottlenecks under high load")
        
        gaps["unclear_aspects"] = [
            "Specific user interface design requirements",
            "Data retention and backup policies",
            "Deployment and hosting preferences",
            "Budget and timeline constraints"
        ]
        
        return gaps
    
    def _synthesize_findings(self, context: Dict, analysis: Dict, gaps: Dict) -> Dict:
        return {
            "context": context,
            "analysis": analysis,
            "gaps": gaps,
            "recommendations": self._generate_recommendations(context, analysis, gaps)
        }
    
    def _generate_recommendations(self, context: Dict, analysis: Dict, gaps: Dict) -> List[str]:
        recommendations = []
        
        if analysis["technical_complexity"] == "High":
            recommendations.append("Consider phased development approach to manage complexity")
            recommendations.append("Implement comprehensive testing strategy including unit, integration, and end-to-end tests")
        
        if context["domain"] in ["Financial Services", "Healthcare"]:
            recommendations.append("Prioritize security and compliance requirements from the start")
            recommendations.append("Implement comprehensive audit logging and monitoring")
        
        if "Real-time Communication" in context["technologies"]:
            recommendations.append("Design for connection management and graceful degradation")
        
        if analysis["scalability_considerations"]:
            recommendations.append("Design with microservices architecture for better scalability")
            recommendations.append("Implement caching strategy early in development")
        
        recommendations.extend([
            "Create detailed user stories and acceptance criteria",
            "Establish clear API contracts between frontend and backend",
            "Plan for comprehensive documentation and knowledge transfer"
        ])
        
        return recommendations
    
    def _generate_markdown_plan(self, findings: Dict) -> str:
        context = findings["context"]
        analysis = findings["analysis"]
        gaps = findings["gaps"]
        recommendations = findings["recommendations"]
        
        markdown = f"""# Deep Research Plan

## Problem Analysis

### Requirement Overview
{context["requirement"]}

### Domain Context
- **Domain**: {context["domain"]}
- **Key Features**: {", ".join(context["key_features"]) if context["key_features"] else "To be defined"}
- **Stakeholders**: {", ".join(context["stakeholders"])}

### Constraints and Requirements
{chr(10).join(f"- {constraint}" for constraint in context["constraints"]) if context["constraints"] else "- No specific constraints identified"}

## Technical Approach

### Architecture Pattern
{analysis["architecture_pattern"]}

### Technology Stack
{chr(10).join(f"- {tech}" for tech in context["technologies"]) if context["technologies"] else "- Technology stack to be determined"}

### Data Flow
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(analysis["data_flow"]))}

### Integration Points
{chr(10).join(f"- {point}" for point in analysis["integration_points"]) if analysis["integration_points"] else "- No external integrations identified"}

## Design Decisions

### Complexity Assessment
- **Technical Complexity**: {analysis["technical_complexity"]}
- **Rationale**: Based on technology stack diversity and feature requirements

### Security Approach
{chr(10).join(f"- {req}" for req in analysis["security_requirements"]) if analysis["security_requirements"] else "- Standard security practices to be implemented"}

### Performance Strategy
{chr(10).join(f"- {req}" for req in analysis["performance_requirements"]) if analysis["performance_requirements"] else "- Performance requirements to be defined"}

## Trade-offs and Alternatives

### Scalability Considerations
{chr(10).join(f"- {consideration}" for consideration in analysis["scalability_considerations"]) if analysis["scalability_considerations"] else "- Scalability requirements to be assessed"}

### Alternative Approaches
- **Monolithic vs Microservices**: Consider starting monolithic for faster initial development, with migration path to microservices
- **Database Choice**: Evaluate SQL vs NoSQL based on data structure and query patterns
- **Frontend Framework**: Balance development speed vs performance requirements

## Risks and Mitigation

### Identified Risks
{chr(10).join(f"- {issue}" for issue in gaps["potential_issues"]) if gaps["potential_issues"] else "- No major risks identified at this stage"}

### Mitigation Strategies
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Assumptions and Gaps
#### Assumptions Made
{chr(10).join(f"- {assumption}" for assumption in gaps["assumptions"])}

#### Missing Requirements
{chr(10).join(f"- {req}" for req in gaps["missing_requirements"]) if gaps["missing_requirements"] else "- All major requirements captured"}

#### Unclear Aspects
{chr(10).join(f"- {aspect}" for aspect in gaps["unclear_aspects"])}

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Set up development environment and project structure
- Implement basic authentication and user management
- Create database schema and initial data models
- Set up CI/CD pipeline

### Phase 2: Core Features (Weeks 3-6)
- Develop primary business logic and APIs
- Implement main user interface components
- Integrate external services and APIs
- Add basic security measures

### Phase 3: Enhancement (Weeks 7-8)
- Implement advanced features and optimizations
- Add comprehensive testing coverage
- Performance tuning and optimization
- Security audit and hardening

### Phase 4: Deployment (Weeks 9-10)
- Production deployment setup
- Monitoring and logging implementation
- Documentation completion
- User acceptance testing and feedback incorporation

### Success Metrics
- Functional requirements met as specified
- Performance benchmarks achieved
- Security standards compliance
- User acceptance criteria satisfied
- Code quality and maintainability standards met

---

*This research plan should be reviewed and refined based on stakeholder feedback and additional requirement clarification.*
"""
        
        return markdown
