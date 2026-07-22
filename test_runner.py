import asyncio
import json
import sys
import os
from pathlib import Path

sys.path.append('c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast')
from server import run_agent_in_subprocess

payload = {
    'student_id': '205400023',
    'name': 'shiva srivastava',
    'metadata': {'batch_year': '2026', 'branch': 'CS'},
    'agent_targets': {'github_handle': 'https://github.com/RahulSharma'}
}

async def run():
    result = await run_agent_in_subprocess(
        'v2', 
        payload, 
        Path('c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/Agent V2/final/config/master_config.xlsx'), 
        Path(''), 
        Path('')
    )
    return result

if __name__ == "__main__":
    result = asyncio.run(run())
    print(json.dumps(result, indent=2))
