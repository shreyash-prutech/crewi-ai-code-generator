"""
TechnicalFeasibilityResearchTool for planning-phase feasibility analysis.

This tool helps planning agents produce structured technical feasibility
findings without performing implementation work or final judging.
"""

from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class TechnicalFeasibilityResearchToolInput(BaseModel):
    """Input schema for TechnicalFeasibilityResearchTool."""
    
    requirement: str = Field(
        ...,
        description="The feature, project, or technical requirement to research for feasibility"
    )
    technical_context: str = Field(
        default="",
        description="Relevant existing architecture, stack, dependencies, or system context"
    )
    constraints: str = Field(
        default="",
        description="Known delivery, security, infrastructure, compliance, or operational constraints"
    )
    focus_areas: str = Field(
        default="architecture, data, integrations, security, operations",
        description="Comma-separated feasibility areas to emphasize during planning research"
    )


class TechnicalFeasibilityResearchTool(BaseTool):
    """
    Tool for producing structured technical feasibility research findings.
    
    Used by planning agents to organize feasibility considerations,
    risks, assumptions, and open questions before implementation begins.
    """
    
    name: str = "technical_feasibility_research_tool"
    description: str = (
        "Produces structured technical feasibility findings for planning. "
        "Use this to analyze implementation considerations, dependencies, "
        "risks, unknowns, and recommended next research steps. "
        "This tool does not write code, implement changes, or make final judgments."
    )
    args_schema: Type[BaseModel] = TechnicalFeasibilityResearchToolInput
    
    def _run(
        self,
        requirement: str,
        technical_context: str = "",
        constraints: str = "",
        focus_areas: str = "architecture, data, integrations, security, operations"
    ) -> str:
        """
        Generate structured technical feasibility research findings.
        
        Args:
            requirement: Requirement to research for technical feasibility
            technical_context: Existing system or architecture context
            constraints: Known constraints affecting feasibility
            focus_areas: Comma-separated areas to emphasize
            
        Returns:
            Structured planning-phase feasibility findings or error description
        """
        try:
            clean_requirement = requirement.strip()
            clean_context = technical_context.strip() or "Not provided"
            clean_constraints = constraints.strip() or "Not provided"
            clean_focus_areas = focus_areas.strip() or "architecture, data, integrations, security, operations"
            
            if not clean_requirement:
                return "Error: Requirement is required for technical feasibility research."
            
            return f"""# Technical Feasibility Research Findings

## Planning Scope
- Requirement under review: {clean_requirement}
- Technical context: {clean_context}
- Known constraints: {clean_constraints}
- Focus areas: {clean_focus_areas}

## Feasibility Dimensions
1. Architecture Fit
   - Assess whether the requirement aligns with the current system boundaries.
   - Identify required services, modules, APIs, or workflow changes.
   - Note coupling concerns and areas where abstractions may be needed.

2. Data and State Impact
   - Identify likely data entities, persistence needs, migrations, and retention concerns.
   - Flag consistency, transactional, indexing, and reporting considerations.
   - Capture unknowns around source-of-truth ownership.

3. Integration Surface
   - Identify external systems, internal services, queues, events, or APIs that may be involved.
   - Note expected contracts, authentication needs, rate limits, and failure handling.
   - Capture dependency availability and version compatibility questions.

4. Security and Compliance
   - Identify authentication, authorization, validation, and audit requirements.
   - Flag sensitive data handling, access boundaries, and least-privilege concerns.
   - Capture compliance or policy questions needing stakeholder confirmation.

5. Operational Readiness
   - Identify observability, logging, monitoring, alerting, and rollback needs.
   - Note scalability, latency, reliability, and deployment considerations.
   - Capture support and maintenance implications.

## Key Assumptions
- The requirement is still in the planning phase.
- No implementation work should be performed from this research output alone.
- Final acceptance, go/no-go decisions, and judging remain outside this tool's scope.
- Additional repository-specific review may be required before engineering begins.

## Primary Risks to Investigate
- Missing or ambiguous acceptance criteria may affect implementation scope.
- Unknown integration contracts may introduce delivery or compatibility risk.
- Data model changes may require migration, backfill, or rollback planning.
- Security requirements may require additional authorization and audit design.
- Operational requirements may affect infrastructure, observability, or deployment plans.

## Open Questions
- Which existing components own the affected business capability?
- What are the required API, data, and user-facing contracts?
- Are there non-functional requirements for performance, availability, or compliance?
- What authentication and authorization rules apply?
- What environments, feature flags, or rollout strategy are expected?

## Recommended Planning Next Steps
- Review existing architecture and identify impacted modules.
- Confirm data ownership and migration requirements.
- Validate integration contracts and external dependency readiness.
- Clarify security, compliance, and observability requirements.
- Convert findings into implementation tasks only after scope is confirmed.

## Explicit Non-Goals
- This tool does not generate implementation code.
- This tool does not modify files, databases, services, or infrastructure.
- This tool does not perform final judging, validation, or approval.
"""
            
        except Exception as e:
            return f"Error generating technical feasibility research findings: {str(e)}"
