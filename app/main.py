from app.api.v1.endpoints import router as v1_router
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI(title="NexClip API")

app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/metrics")
async def metrics():
    return JSONResponse(content={"message": "Metrics not implemented"})
