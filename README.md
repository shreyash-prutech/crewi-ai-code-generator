# crewi-ai-code-generator

# CodeGenereator Crew

Welcome to the CodeGenereator Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

```mermaid
graph TD
    User([User Requirement]) --> Init[init_development]
    
    subgraph Flow Orchestrator: SoftwareDevFlow
        Init --> Phase1[run_planning]
        Phase1 --> Phase2[run_engineering]
        Phase2 --> Phase3[run_validation]
    end

    subgraph Phase 1: PlanningCrew
        Phase1 --> Architect[Architect Agent]
        Architect --> Spec[Technical Spec / Plan]
    end

    subgraph Phase 2: EngineeringCrew
        Spec --> DB[DB Agent]
        DB --> Backend[Backend Agent]
        Backend --> Frontend[Frontend Agent]
    end

    subgraph Phase 3: JudgeCrew
        DB & Backend & Frontend --> Judge[Judge Agent]
        Judge --> Save[FileWriteTool]
        Judge --> Report[Final Audit Report]
    end

    Save --> Disk[(dist/ folder)]
    Report --> FinalState([Completed State])
```

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/code_genereator/config/agents.yaml` to define your agents
- Modify `src/code_genereator/config/tasks.yaml` to define your tasks
- Modify `src/code_genereator/crew.py` to add your own logic, tools and specific args
- Modify `src/code_genereator/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the code_genereator Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The code_genereator Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the CodeGenereator Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
