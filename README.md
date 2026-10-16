Our group used AI selectively. Below is a list of the parts where AI was used：
1. developer_agent.py — SYSTEM_PROMPT
   The English SYSTEM_PROMPT in developer_agent.py was written with AI assistance.
2. test_generated_navigation_logic.py — unittest framework
   At first we planned to write a simple for-loop with a few if-else prints. AI suggested using unittest so the result would show clearly.
3. analyst_agent.py — SYSTEM_PROMPT 和 validate_requirements()
   The SYSTEM_PROMPT in analyst_agent.py and the validate_requirements() function were written with AI assistance.
4. run_analyst.py
   In run_analyst.py, the lines:
    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "requirements.json"
   AI suggested mkdir(parents=True, exist_ok=True), the script could be re-run many times without crashing.
