#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
職業分類判定クラス（RAG構成）
Google Gemini API を使用
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity


class OccupationClassifier:
    """
    職業分類判定クラス
    Google Gemini Embeddings と Gemini を使用したRAG構成で職業分類を判定します。
    シングルトンパターンで実装（インスタンスの再利用）
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """シングルトンパターン実装"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str = None, api_key: str = None):
        """
        初期化処理
        
        Args:
            csv_path: CSVファイルのパス（Noneの場合はダミーデータを使用）
            api_key: Gemini APIキー（Noneの場合は環境変数から取得）
        """
        # 既に初期化済みの場合はスキップ
        if hasattr(self, '_initialized'):
            return
        
        # Gemini APIキーの取得と検証
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEYが設定されていません。\n"
                "環境変数を設定してください。"
            )
        
        # Gemini APIの設定
        genai.configure(api_key=self.api_key)
        
        # Embeddingモデルの指定
        self.embedding_model = "models/text-embedding-004"
        
        # LLMモデルの指定
        self.llm_model = "models/gemini-2.5-flash"
        
        # GenerativeModelの初期化
        self.model = genai.GenerativeModel(self.llm_model)
        
        # データのロード
        self.data = self._load_data(csv_path)
        
        # Embeddingsの初期化（遅延評価）
        self.embeddings = None
        self.embedding_texts = None
        
        self._initialized = True
        print(f"OccupationClassifier initialized with {len(self.data)} occupations")
    
    def _load_data(self, csv_path: str = None) -> pd.DataFrame:
        """
        職業分類データの読み込み
        
        Args:
            csv_path: CSVファイルのパス（Noneの場合はダミーデータを作成）
        
        Returns:
            職業分類データのDataFrame
        """
        if csv_path and os.path.exists(csv_path):
            # CSVファイルから読み込み
            print(f"CSVファイルを読み込んでいます: {csv_path}")
            return pd.read_csv(csv_path)
        else:
            # ダミーデータの作成
            print("ダミーデータを使用しています...")
            dummy_data = [
                {
                    "code": "11",
                    "name": "管理的職業従事者",
                    "description": "会社役員、企業の部課長、管理職。組織の経営方針の決定や業務の管理・監督を行う。"
                },
                {
                    "code": "21",
                    "name": "一般事務従事者",
                    "description": "庶務、人事、経理、総務、秘書など。エクセル集計、書類作成、データ入力、電話応対などのオフィスワーク。"
                },
                {
                    "code": "25",
                    "name": "会計事務従事者",
                    "description": "経理担当者、会計係、簿記担当。会社の会計業務、伝票処理、決算業務、財務諸表作成。"
                },
                {
                    "code": "32",
                    "name": "保安職業従事者",
                    "description": "自衛官、警察官、消防隊員、消防士、海上保安官、警備員。火災の消火活動、救急救命、治安維持、災害対応。"
                },
                {
                    "code": "35",
                    "name": "介護サービス職業従事者",
                    "description": "介護福祉士、ホームヘルパー、ケアワーカー。高齢者や障害者の身体介護、生活援助、介護施設での勤務。"
                },
                {
                    "code": "41",
                    "name": "販売従事者",
                    "description": "小売店員、営業職、セールス、shop店員。商品販売、接客、レジ業務、在庫管理、顧客対応。"
                },
                {
                    "code": "52",
                    "name": "飲食物調理従事者",
                    "description": "調理師、コック、料理人、シェフ、板前。レストラン、ホテル、食堂などでの料理の調理。"
                },
                {
                    "code": "61",
                    "name": "農林漁業従事者",
                    "description": "農家、漁師、林業作業者。農作物の栽培、漁業、林業、畜産などの第一次産業。"
                },
                {
                    "code": "71",
                    "name": "製造・加工処理従事者",
                    "description": "工場作業員、製造オペレーター、組立工。製品の製造、機械操作、品質検査、組立作業。"
                },
                {
                    "code": "81",
                    "name": "建設・採掘従事者",
                    "description": "大工、建築作業員、土木作業員、鉱山作業員。建設現場での建築、土木工事、採掘作業。"
                },
                {
                    "code": "91",
                    "name": "運搬・清掃・包装等従事者",
                    "description": "トラック運転手、配達員、清掃員、倉庫作業員。荷物の運搬、清掃業務、梱包作業。"
                },
                {
                    "code": "12",
                    "name": "情報処理・通信技術者",
                    "description": "システムエンジニア、プログラマー、SE、ソフトウェア開発者、Webエンジニア、アプリ開発。コーディング、システム設計、データベース管理。"
                },
                {
                    "code": "14",
                    "name": "建築・土木・測量技術者",
                    "description": "建築士、土木技術者、測量士、設計士。建物や構造物の設計、測量、施工管理。"
                },
                {
                    "code": "15",
                    "name": "医師・歯科医師・獣医師・薬剤師",
                    "description": "医師、歯科医、獣医、薬剤師。診療、治療、処方、手術、健康管理、薬の調剤。"
                },
                {
                    "code": "16",
                    "name": "保健師・助産師・看護師",
                    "description": "看護師、保健師、助産師。患者のケア、健康指導、医療補助、病院や診療所での勤務。"
                },
                {
                    "code": "17",
                    "name": "教員",
                    "description": "小学校教員、中学校教員、高校教員、大学教授、塾講師、教師。学校での授業、教育、生徒指導。"
                },
            ]
            return pd.DataFrame(dummy_data)
    
    def create_embeddings(self, force_recreate: bool = False):
        """
        職業データのEmbeddingsを作成（キャッシュ機能付き）
        
        Args:
            force_recreate: Trueの場合、キャッシュを無視して再作成
        """
        cache_file = "data/embeddings_cache.npy"
        
        # キャッシュファイルが存在し、強制再作成でない場合は読み込み
        if not force_recreate and os.path.exists(cache_file):
            try:
                print(f"キャッシュからEmbeddingsを読み込んでいます: {cache_file}")
                self.embeddings = np.load(cache_file)
                
                # embedding_textsも再構築
                self.embedding_texts = (
                    self.data['name'] + '。' + self.data['description']
                ).tolist()
                
                print(f"Embeddingsキャッシュ読み込み完了 (shape: {self.embeddings.shape})")
                print(f"💡 API呼び出しを節約しました！（{len(self.data)}件のEmbedding作成をスキップ）")
                return
                
            except Exception as e:
                print(f"⚠️ キャッシュ読み込み失敗: {e}")
                print("新しくEmbeddingsを作成します...")
        
        # キャッシュがない、または強制再作成の場合
        if self.embeddings is not None:
            print("Embeddingsは既に作成済みです")
            return
        
        print(f"Embeddingsを作成しています...（{len(self.data)}件）")
        print("⚠️ 初回のみ時間がかかります。次回からはキャッシュを使用します。")
        
        # 各職業のテキストを結合
        self.embedding_texts = (
            self.data['name'] + '。' + self.data['description']
        ).tolist()
        
        # Embeddingsを作成
        embeddings_list = []
        
        for i, text in enumerate(self.embedding_texts):
            if (i + 1) % 50 == 0:
                print(f"  進捗: {i + 1}/{len(self.embedding_texts)}")
            
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text
                )
                embeddings_list.append(result['embedding'])
            except Exception as e:
                print(f"  エラー (職業 {i}): {e}")
                raise
        
        self.embeddings = np.array(embeddings_list)
        print(f"Embeddings作成完了 (shape: {self.embeddings.shape})")
        
        # キャッシュファイルに保存
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            np.save(cache_file, self.embeddings)
            print(f"✅ Embeddingsをキャッシュに保存しました: {cache_file}")
            print(f"💡 次回起動時はAPI呼び出しなしで高速起動できます！")
        except Exception as e:
            print(f"⚠️ キャッシュ保存失敗（無視して続行）: {e}")
            
        except Exception as e:
            raise RuntimeError(f"Embeddings作成中にエラーが発生しました: {str(e)}")
    
    def search_candidates(self, user_input: str, top_k: int = 5) -> List[Dict]:
        """
        ユーザー入力から類似度の高い職業候補を検索
        
        Args:
            user_input: ユーザーの自由記述入力
            top_k: 取得する候補数（デフォルト: 5）
        
        Returns:
            類似度の高い職業候補のリスト
        """
        # Embeddingsが未作成の場合は作成
        if self.embeddings is None:
            self.create_embeddings()
        
        try:
            # ユーザー入力をベクトル化
            result = genai.embed_content(
                model=self.embedding_model,
                content=user_input,
                task_type="retrieval_query"
            )
            user_embedding = np.array([result['embedding']])
            
            # コサイン類似度を計算
            similarities = cosine_similarity(user_embedding, self.embeddings)[0]
            
            # 類似度の高い順にソート
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # 候補を作成
            candidates = []
            for idx in top_indices:
                candidates.append({
                    "code": self.data.iloc[idx]["code"],
                    "name": self.data.iloc[idx]["name"],
                    "description": self.data.iloc[idx]["description"],
                    "similarity": float(similarities[idx])
                })
            
            return candidates
            
        except Exception as e:
            raise RuntimeError(f"候補検索中にエラーが発生しました: {str(e)}")
    
    def decide_class(self, user_input: str, candidates: List[Dict]) -> Dict:
        """
        Gemini を使用して最終的な職業分類を判定
        
        Args:
            user_input: ユーザーの自由記述入力
            candidates: 検索された候補リスト
        
        Returns:
            判定結果（code, name, reason）
        """
        # User Prompt の作成
        candidates_text = "\n".join([
            f"- コード: {c['code']}, 名称: {c['name']}, 説明: {c['description']}"
            for c in candidates
        ])
        
        prompt = f"""あなたは職業分類の専門家です。
ユーザーの入力と、候補となる職業分類リストを比較し、最も適切な職業分類を1つ選択してください。

【ユーザーの入力】
{user_input}

【候補となる職業分類】
{candidates_text}

上記の候補から最も適切な職業分類を1つ選択し、必ず以下のJSON形式で回答してください：
{{
  "code": "職業コード",
  "name": "職業名",
  "reason": "この職業を選択した理由（日本語で簡潔に）"
}}"""
        
        try:
            # Gemini での判定（JSON Modeを使用）
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            # レスポンスの解析
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Gemini での判定中にエラーが発生しました: {str(e)}")
    
    def classify(self, user_input: str) -> Dict:
        """
        職業分類判定のメイン処理
        
        Args:
            user_input: ユーザーの自由記述入力
        
        Returns:
            判定結果（code, name, reason, candidates を含む）
        """
        # Step 1: 候補検索 (Retrieval)
        candidates = self.search_candidates(user_input, top_k=5)
        
        # Step 2: 最終判定 (Generation)
        result = self.decide_class(user_input, candidates)
        
        # 結果に候補リストを追加
        result['candidates'] = candidates
        result['user_input'] = user_input
        
        return result
