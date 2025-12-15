"""
Pydantic models for API request/response
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    """職業候補モデル"""
    code: str = Field(..., description="職業コード")
    name: str = Field(..., description="職業名")
    description: str = Field(..., description="職業の説明")
    similarity: float = Field(..., description="類似度スコア")


class ClassifyRequest(BaseModel):
    """職業分類判定リクエストモデル"""
    user_input: str = Field(..., min_length=1, max_length=500, description="ユーザーの自由記述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "消防車に乗って火を消す仕事"
            }
        }


class ClassifyResponse(BaseModel):
    """職業分類判定レスポンスモデル"""
    code: str = Field(..., description="判定された職業コード")
    name: str = Field(..., description="判定された職業名")
    reason: str = Field(..., description="判定理由")
    candidates: List[Candidate] = Field(..., description="検索された候補リスト")
    user_input: str = Field(..., description="ユーザーの入力")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "32",
                "name": "保安職業従事者",
                "reason": "消防車に乗って火を消す仕事は、消防隊員・消防士の業務に該当します",
                "candidates": [
                    {
                        "code": "32",
                        "name": "保安職業従事者",
                        "description": "自衛官、警察官、消防隊員...",
                        "similarity": 0.89
                    }
                ],
                "user_input": "消防車に乗って火を消す仕事"
            }
        }


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンスモデル"""
    status: str = Field(..., description="サービスステータス")
    message: str = Field(..., description="メッセージ")
