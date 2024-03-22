### 开始

`conda create -n openvoice python==3.10.12`

`conda activate openvoice`

`pip install -r requirements.txt`

`unzip ~/autodl-fs/checkpoints_1226.zip -d /home/nexClip-voice`

`uvicorn app.main:app --reload`
