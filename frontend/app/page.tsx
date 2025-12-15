'use client';

import { useState } from 'react';

interface Candidate {
  code: string;
  name: string;
  description: string;
  similarity: number;
}

interface ClassifyResponse {
  code: string;
  name: string;
  reason: string;
  candidates: Candidate[];
  user_input: string;
}

export default function Home() {
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClassifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!userInput.trim()) {
      setError('職業の説明を入力してください');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/classify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: userInput }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '判定に失敗しました');
      }

      const data: ClassifyResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期しないエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const exampleInputs = [
    '消防車に乗って火を消す仕事',
    'エクセルの集計業務',
    'プログラミングでWebアプリを作っています',
    '会社の経理を担当しています',
    'お店でレジ打ちをしています',
  ];

  return (
    <main className="min-h-screen p-4 md:p-8">
      {/* 背景装飾 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        {/* ヘッダー */}
        <header className="text-center mb-12 animate-float">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 gradient-text">
            職業分類判定システム
          </h1>
          <p className="text-gray-300 text-lg">
            自由記述から適切な職業分類を判定します（RAG構成）
          </p>
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 glass rounded-full text-sm">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-gray-300">Google Gemini API (text-embedding-004 + gemini-1.5-flash)</span>
          </div>
        </header>

        {/* 入力フォーム */}
        <div className="glass rounded-2xl p-6 md:p-8 mb-8 card">
          <form onSubmit={handleSubmit}>
            <label htmlFor="user-input" className="block text-lg font-semibold mb-3 text-blue-300">
              あなたの職業を自由に説明してください
            </label>
            <textarea
              id="user-input"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="例: 消防車に乗って火を消す仕事"
              className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
              rows={4}
              disabled={loading}
            />

            {/* サンプル入力 */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">サンプル入力:</p>
              <div className="flex flex-wrap gap-2">
                {exampleInputs.map((example, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setUserInput(example)}
                    className="px-3 py-1.5 text-sm bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg transition-all hover:scale-105"
                    disabled={loading}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>

            {/* 送信ボタン */}
            <button
              type="submit"
              disabled={loading || !userInput.trim()}
              className="mt-6 w-full btn-primary text-white font-semibold py-4 px-6 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-3">
                  <div className="spinner"></div>
                  <span>判定中...</span>
                </span>
              ) : (
                <span>🔍 職業分類を判定する</span>
              )}
            </button>
          </form>
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="glass rounded-xl p-4 mb-8 border-l-4 border-red-500 animate-pulse-glow">
            <div className="flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              <div>
                <p className="font-semibold text-red-400">エラー</p>
                <p className="text-gray-300">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* 結果表示 */}
        {result && (
          <div className="space-y-6">
            {/* 判定結果 */}
            <div className="glass rounded-2xl p-6 md:p-8 card animate-pulse-glow">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <span className="text-3xl">✅</span>
                <span className="gradient-text">判定結果</span>
              </h2>

              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-mono text-2xl font-bold">
                    {result.code}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-blue-300 mb-2">
                      {result.name}
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      {result.reason}
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-700">
                  <p className="text-sm text-gray-400">
                    <span className="font-semibold">入力内容:</span> {result.user_input}
                  </p>
                </div>
              </div>
            </div>

            {/* 候補リスト */}
            <div className="glass rounded-2xl p-6 md:p-8 card">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>類似職業候補（上位5件）</span>
              </h3>

              <div className="space-y-3">
                {result.candidates.map((candidate, index) => (
                  <div
                    key={index}
                    className="bg-gray-900/50 rounded-xl p-4 border border-gray-700 hover:border-blue-500 transition-all card"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-gray-400">
                          #{index + 1}
                        </span>
                        <span className="px-3 py-1 bg-gray-800 rounded-lg font-mono text-sm">
                          {candidate.code}
                        </span>
                        <span className="font-semibold text-blue-300">
                          {candidate.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-800 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all"
                            style={{ width: `${candidate.similarity * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-mono text-cyan-400">
                          {(candidate.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-400 ml-11">
                      {candidate.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* フッター */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Powered by Google Gemini API (text-embedding-004 + gemini-1.5-flash)</p>
          <p className="mt-2">RAG構成による高精度な職業分類判定システム</p>
        </footer>
      </div>
    </main>
  );
}
