"""
CLI - Command-line interface
"""

import argparse
import sys
import os


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="conductor",
        description="Conductor - AI Agent Orchestration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # new command
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("name", help="Project name")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Run an agent file")
    run_parser.add_argument("file", help="Agent file to run")
    
    # dev command
    dev_parser = subparsers.add_parser("dev", help="Start development server")
    dev_parser.add_argument("--port", type=int, default=8000, help="Port number")
    
    # deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy agents")
    deploy_parser.add_argument("--target", choices=["docker", "kubernetes"], default="docker")
    
    # version command
    subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    if args.command == "new":
        create_project(args.name)
    elif args.command == "run":
        run_agent(args.file)
    elif args.command == "dev":
        start_dev_server(args.port)
    elif args.command == "deploy":
        deploy(args.target)
    elif args.command == "version":
        from conductor import __version__
        print(f"Conductor v{__version__}")
    else:
        parser.print_help()


def create_project(name: str):
    """Create a new Conductor project."""
    os.makedirs(name, exist_ok=True)
    
    # Create main agent file
    agent_code = '''"""
My Conductor Agent
"""

import asyncio
from conductor import Agent

agent = Agent(
    name="assistant",
    model="gpt-4o",
    instructions="You are a helpful assistant."
)

async def main():
    response = await agent.run("Hello! What can you help me with?")
    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open(os.path.join(name, "agent.py"), "w") as f:
        f.write(agent_code)
    
    # Create requirements.txt
    with open(os.path.join(name, "requirements.txt"), "w") as f:
        f.write("conductor-agents\n")
    
    # Create .env.example
    with open(os.path.join(name, ".env.example"), "w") as f:
        f.write("OPENAI_API_KEY=sk-...\n")
    
    print(f"Created project: {name}")
    print(f"\nNext steps:")
    print(f"  cd {name}")
    print(f"  pip install -r requirements.txt")
    print(f"  export OPENAI_API_KEY=sk-...")
    print(f"  python agent.py")


def run_agent(file: str):
    """Run an agent file."""
    import subprocess
    subprocess.run([sys.executable, file])


def start_dev_server(port: int):
    """Start development server with hot reload."""
    print(f"Starting Conductor dev server on port {port}...")
    print("Development server with live hot reload is scheduled for v0.2.0.")
    print("In the meantime, execute agents directly using: python agent.py (or 'conductor run agent.py')")


def deploy(target: str):
    """Deploy agents to target platform."""
    print(f"Deploying agents to target: {target}...")
    print("Automated deployment command is scheduled for v0.2.0.")
    print("Refer to docs/DEPLOYMENT.md for containerization and production patterns.")


if __name__ == "__main__":
    main()
