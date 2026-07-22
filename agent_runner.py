import os
import sys
import json
import asyncio
from pathlib import Path

# Load dotenv if available to populate env variables
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

ROOT_DIR = Path(__file__).resolve().parent

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Missing agent version argument (v1 or v2)"}))
        sys.exit(1)

    version = sys.argv[1].strip().lower()
    
    # Resolve directories
    if version == "v2":
        agent_dir = ROOT_DIR / "Agent V2"
    else:
        agent_dir = ROOT_DIR / "agent"
        
    core_dir = agent_dir / "final" / "core"
    
    # Load version-specific environment variables
    if HAS_DOTENV:
        env_path = agent_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        resugent_env = agent_dir / "resugent" / ".env"
        if resugent_env.exists():
            load_dotenv(dotenv_path=resugent_env)
            
    # Modify sys.path: prioritize the current agent's core and base directories
    sys.path.insert(0, str(core_dir))
    sys.path.insert(1, str(agent_dir))
    
    # Read payload from stdin
    try:
        input_data = json.loads(sys.stdin.read())
        student_payload = input_data["student_payload"]
        config_path = input_data["config_path"]
        benchmarks_data = input_data.get("benchmarks_data", {})
        ontology_data = input_data.get("ontology_data", {})
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to parse stdin payload: {e}"}))
        sys.exit(1)
        
    try:
        import config_loader
        import orchestrator
        
        # Load master config
        master_configuration = config_loader.load_master_config(str(config_path))
        
        # Run orchestrator async evaluation
        result = await orchestrator.evaluate_student(
            student_payload,
            master_configuration,
            benchmarks=benchmarks_data,
            ontology=ontology_data
        )
        print(json.dumps({"status": "success", "result": result}))
    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
