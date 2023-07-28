import asyncio
import subprocess
import sys

async def run_script_async(script):
    print(f"Running {script}...")
    process = await asyncio.create_subprocess_exec(sys.executable, script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    print(f"{script} finished with return code {process.returncode}")
    if stderr:
        print(f"Error in {script}: {stderr.decode()}")

async def main():
    script_files = ["prizepicks_nba.py", "pinnacle_nba.py", "draftkings_nba.py"]
    tasks = [run_script_async(script) for script in script_files]
    
    await asyncio.gather(*tasks)
    
    # Run final_python.py after all the other scripts have finished
    await run_script_async("optimizer_nba_data_cleaning.py")

if __name__ == "__main__":
    asyncio.run(main())
