### 开始

conda create -n openvoice python==3.10.12
conda activate openvoice
pip install -r requirements.txt
uvicorn app.main:app --reload
