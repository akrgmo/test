"""
プロンプト最適化支援 API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from analyzer import analyze_prompt

app = FastAPI(
    title="プロンプト最適化支援ツール",
    description="LLM向けプロンプトの分析と最適化提案を行うAPIです",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    """プロンプト分析リクエスト"""
    prompt: str


class AnalysisResponse(BaseModel):
    """分析結果レスポンス"""
    score: int
    issues: list
    suggestions: list
    structure: dict
    optimized_prompt: str | None


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: PromptRequest):
    """
    プロンプトを分析して最適化提案を返す

    - **prompt**: 分析対象のプロンプト文字列
    """
    result = analyze_prompt(request.prompt)
    return AnalysisResponse(**result)


@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}


# 静的ファイルの配信
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_index():
        """フロントエンドのindex.htmlを配信"""
        return FileResponse(os.path.join(frontend_path, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
