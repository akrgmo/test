"""
プロンプト分析・最適化モジュール
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalysisResult:
    """分析結果"""
    score: int  # 0-100
    issues: list[dict]
    suggestions: list[dict]
    structure: dict
    optimized_prompt: Optional[str]


class PromptAnalyzer:
    """プロンプト分析クラス"""

    # 曖昧な表現パターン
    VAGUE_PATTERNS = [
        (r'適切に|適切な', '「適切」の具体的な基準を明示してください'),
        (r'良い|良く', '「良い」の定義や評価基準を具体的に示してください'),
        (r'など', '「など」を具体的な例に置き換えてください'),
        (r'いい感じ', '具体的にどのような状態を期待するか明示してください'),
        (r'できれば|可能であれば', '優先度を明確にするか、条件を具体化してください'),
        (r'たぶん|おそらく', '不確実な表現を避け、明確な指示にしてください'),
        (r'とか', '選択肢を明確に列挙してください'),
        (r'いくつか', '具体的な数を指定してください'),
        (r'簡単に|簡潔に', '文字数や段落数など具体的な制限を設けてください'),
    ]

    # 構造要素のキーワード
    ROLE_KEYWORDS = [
        'あなたは', 'として', 'の役割', 'のように振る舞', 'になって',
        'You are', 'Act as', 'Pretend to be', 'role of'
    ]

    CONTEXT_KEYWORDS = [
        '背景', 'コンテキスト', '状況', '前提', '条件として',
        'Background', 'Context', 'Given that', 'Assuming'
    ]

    OUTPUT_FORMAT_KEYWORDS = [
        '形式で', 'フォーマット', '以下の形で', '出力は', '回答は',
        'JSON', 'Markdown', 'リスト形式', '箇条書き', 'テーブル',
        'format', 'output as', 'respond in', 'provide as'
    ]

    EXAMPLE_KEYWORDS = [
        '例:', '例えば', 'サンプル', '具体例',
        'Example:', 'For example', 'Sample:', 'e.g.'
    ]

    def analyze(self, prompt: str) -> AnalysisResult:
        """プロンプトを分析して結果を返す"""
        issues = []
        suggestions = []
        score = 100

        # 構造分析
        structure = self._analyze_structure(prompt)

        # 長さチェック
        length_result = self._check_length(prompt)
        if length_result:
            issues.append(length_result)
            score -= length_result.get('penalty', 10)

        # 曖昧表現チェック
        vague_results = self._check_vague_expressions(prompt)
        for result in vague_results:
            issues.append(result)
            score -= 5

        # 構造要素チェック
        structure_suggestions = self._check_structure_elements(structure)
        suggestions.extend(structure_suggestions)
        score -= len(structure_suggestions) * 5

        # 改善提案
        improvement_suggestions = self._generate_suggestions(prompt, structure)
        suggestions.extend(improvement_suggestions)

        # スコアを0-100に正規化
        score = max(0, min(100, score))

        # 最適化されたプロンプトを生成
        optimized = self._generate_optimized_prompt(prompt, structure, issues)

        return AnalysisResult(
            score=score,
            issues=issues,
            suggestions=suggestions,
            structure=structure,
            optimized_prompt=optimized
        )

    def _analyze_structure(self, prompt: str) -> dict:
        """プロンプトの構造を分析"""
        return {
            'has_role': any(kw in prompt for kw in self.ROLE_KEYWORDS),
            'has_context': any(kw in prompt for kw in self.CONTEXT_KEYWORDS),
            'has_output_format': any(kw in prompt for kw in self.OUTPUT_FORMAT_KEYWORDS),
            'has_examples': any(kw in prompt for kw in self.EXAMPLE_KEYWORDS),
            'length': len(prompt),
            'line_count': len(prompt.split('\n')),
            'has_clear_task': self._has_clear_task(prompt),
        }

    def _has_clear_task(self, prompt: str) -> bool:
        """明確なタスク指示があるかチェック"""
        task_patterns = [
            r'してください', r'教えて', r'作成して', r'生成して', r'説明して',
            r'答えて', r'書いて', r'考えて', r'提案して', r'分析して',
            r'please', r'create', r'generate', r'explain', r'write',
            r'analyze', r'help me', r'how to', r'what is'
        ]
        return any(re.search(p, prompt, re.IGNORECASE) for p in task_patterns)

    def _check_length(self, prompt: str) -> Optional[dict]:
        """プロンプトの長さをチェック"""
        length = len(prompt)

        if length < 20:
            return {
                'type': 'length',
                'severity': 'warning',
                'message': 'プロンプトが短すぎます。より具体的な指示を追加してください。',
                'penalty': 20
            }
        elif length < 50:
            return {
                'type': 'length',
                'severity': 'info',
                'message': 'プロンプトがやや短いです。コンテキストや詳細を追加することを検討してください。',
                'penalty': 10
            }
        elif length > 5000:
            return {
                'type': 'length',
                'severity': 'warning',
                'message': 'プロンプトが非常に長いです。要点を整理することを検討してください。',
                'penalty': 10
            }
        return None

    def _check_vague_expressions(self, prompt: str) -> list[dict]:
        """曖昧な表現をチェック"""
        results = []
        for pattern, suggestion in self.VAGUE_PATTERNS:
            matches = re.findall(pattern, prompt)
            if matches:
                results.append({
                    'type': 'vague_expression',
                    'severity': 'warning',
                    'message': f'曖昧な表現「{matches[0]}」が見つかりました',
                    'suggestion': suggestion
                })
        return results

    def _check_structure_elements(self, structure: dict) -> list[dict]:
        """構造要素の不足をチェック"""
        suggestions = []

        if not structure['has_role']:
            suggestions.append({
                'type': 'structure',
                'element': 'role',
                'message': '役割設定の追加を検討してください',
                'example': '例: 「あなたはプロのコピーライターです」'
            })

        if not structure['has_output_format']:
            suggestions.append({
                'type': 'structure',
                'element': 'output_format',
                'message': '出力形式の指定を追加することを検討してください',
                'example': '例: 「箇条書きで回答してください」「JSON形式で出力してください」'
            })

        if not structure['has_examples'] and structure['length'] > 100:
            suggestions.append({
                'type': 'structure',
                'element': 'examples',
                'message': '具体例を追加すると、期待する出力がより明確になります',
                'example': '例: 「例: 入力「〇〇」→ 出力「△△」」'
            })

        return suggestions

    def _generate_suggestions(self, prompt: str, structure: dict) -> list[dict]:
        """追加の改善提案を生成"""
        suggestions = []

        # 疑問形だが具体性がない場合
        if '?' in prompt or '？' in prompt:
            if structure['length'] < 100 and not structure['has_context']:
                suggestions.append({
                    'type': 'improvement',
                    'message': '質問に背景情報を追加すると、より適切な回答が得られます',
                    'example': '質問の前に「〇〇の文脈で」「〇〇を目的として」などを追加'
                })

        # 複数のタスクが混在している可能性
        task_indicators = ['また', 'さらに', 'それから', 'そして', 'And also', 'Additionally']
        if any(ind in prompt for ind in task_indicators):
            suggestions.append({
                'type': 'improvement',
                'message': '複数のタスクを含んでいる場合、番号付きリストで整理すると効果的です',
                'example': '1. 最初のタスク\n2. 次のタスク\n3. 最後のタスク'
            })

        return suggestions

    def _generate_optimized_prompt(self, prompt: str, structure: dict, issues: list) -> str:
        """最適化されたプロンプト案を生成"""
        parts = []

        # 役割設定を追加（なければ）
        if not structure['has_role']:
            parts.append('【役割】\nあなたは専門家として、以下の依頼に対応してください。\n')

        # 元のプロンプト
        parts.append('【タスク】\n' + prompt + '\n')

        # 出力形式を追加（なければ）
        if not structure['has_output_format']:
            parts.append('\n【出力形式】\n- 分かりやすく構造化して回答してください\n- 重要なポイントは箇条書きで示してください')

        return '\n'.join(parts)


# シングルトンインスタンス
analyzer = PromptAnalyzer()


def analyze_prompt(prompt: str) -> dict:
    """プロンプトを分析してJSON形式で結果を返す"""
    result = analyzer.analyze(prompt)
    return {
        'score': result.score,
        'issues': result.issues,
        'suggestions': result.suggestions,
        'structure': result.structure,
        'optimized_prompt': result.optimized_prompt
    }
