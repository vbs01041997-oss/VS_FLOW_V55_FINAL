@echo off
cd /d "%~dp0"
python -m streamlit run VS_FLOW_V55_FINAL.py --server.headless false --browser.gatherUsageStats false
pause
