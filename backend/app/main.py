#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Backend for Occupation Classification System
職業分類判定システムのバックエンドAPI
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import ClassifyRequest, ClassifyResponse, HealthResponse
from .classifier import OccupationClassifier

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

# グローバル変数
classifier = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理
    起動時にClassifierを初期化し、Embeddingsを事前作成
    """
    global classifier
    
    logger.info("Starting up application...")
    
    try:
        # Classifierの初期化
        classifier = OccupationClassifier()
        
        # Embeddingsの事前作成
        classifier.create_embeddings()
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize classifier: {e}")
        raise
    
    yield
    
    # シャットダウン処理
    logger.info("Shutting down application...")


# FastAPIアプリケーションの作成
app = FastAPI(
    title="職業分類判定API",
    description="自由記述から職業分類コードを判定するRAGシステム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """
    ルートエンドポイント
    """
    return {
        "status": "ok",
        "message": "職業分類判定API - /docs でAPI仕様を確認できます"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classifier is not initialized"
        )
    
    return {
        "status": "healthy",
        "message": f"職業分類データ {len(classifier.data)} 件をロード済み"
    }


@app.post("/api/classify", response_model=ClassifyResponse)
async def classify_occupation(request: ClassifyRequest):
    """
    職業分類判定エンドポイント
    
    ユーザーの自由記述から適切な職業分類を判定します。
    
    Args:
        request: ClassifyRequest - ユーザー入力を含むリクエストボディ
    
    Returns:
        ClassifyResponse - 判定結果（コード、職業名、理由、候補リスト）
    
    Raises:
        HTTPException: 500 - 判定処理中のエラー
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classifier is not initialized"
        )
    
    try:
        logger.info(f"Classification request: {request.user_input[:50]}...")
        
        # 職業分類判定の実行
        result = classifier.classify(request.user_input)
        
        logger.info(f"Classification result: [{result['code']}] {result['name']}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"判定処理中にエラーが発生しました: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="予期しないエラーが発生しました"
        )


if __name__ == "__main__":
    import uvicorn
    
    # 開発用サーバーの起動
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
