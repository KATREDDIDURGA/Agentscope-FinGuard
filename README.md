 # Windows: venv\Scripts\activate 

 pip install -r requirements.txt 

 uvicorn app.main:app --reload
 streamlit run app/ui/ui.py
