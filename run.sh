ROOT_PATH="/"
FINAL_BASE_PATH="${ROOT_PATH}${TIMEGEN_BASE_PATH}"
streamlit run TIMEGEN_Demo.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false --server.baseUrlPath=${FINAL_BASE_PATH} --server.enableWebsocketCompression=false