// DOM要素
const promptInput = document.getElementById('prompt-input');
const charCount = document.getElementById('char-count');
const analyzeBtn = document.getElementById('analyze-btn');
const resultSection = document.getElementById('result-section');
const scoreValue = document.getElementById('score-value');
const scoreTitle = document.getElementById('score-title');
const scoreMessage = document.getElementById('score-message');
const structureBadges = document.getElementById('structure-badges');
const issuesList = document.getElementById('issues-list');
const suggestionsList = document.getElementById('suggestions-list');
const optimizedPrompt = document.getElementById('optimized-prompt');
const copyBtn = document.getElementById('copy-btn');
const issuesSection = document.getElementById('issues-section');
const suggestionsSection = document.getElementById('suggestions-section');

// 文字数カウント
promptInput.addEventListener('input', () => {
    charCount.textContent = `${promptInput.value.length} 文字`;
});

// 分析ボタンクリック
analyzeBtn.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();

    if (!prompt) {
        alert('プロンプトを入力してください');
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '分析中...';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });

        if (!response.ok) {
            throw new Error('分析に失敗しました');
        }

        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Error:', error);
        alert('分析中にエラーが発生しました: ' + error.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '分析する';
    }
});

// 結果を表示
function displayResult(result) {
    resultSection.classList.remove('hidden');

    // スコア表示
    scoreValue.textContent = result.score;
    updateScoreDisplay(result.score);

    // 構造バッジ
    displayStructureBadges(result.structure);

    // 問題表示
    displayIssues(result.issues);

    // 提案表示
    displaySuggestions(result.suggestions);

    // 最適化されたプロンプト
    optimizedPrompt.textContent = result.optimized_prompt || '';

    // スクロール
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// スコアに応じた表示を更新
function updateScoreDisplay(score) {
    const circle = document.querySelector('.score-circle');

    if (score >= 80) {
        scoreTitle.textContent = '優秀なプロンプト';
        scoreMessage.textContent = 'このプロンプトは構造がしっかりしており、明確な指示が含まれています。';
        circle.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)';
    } else if (score >= 60) {
        scoreTitle.textContent = '良好なプロンプト';
        scoreMessage.textContent = '基本的な要素は含まれていますが、いくつか改善の余地があります。';
        circle.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
    } else if (score >= 40) {
        scoreTitle.textContent = '改善が必要';
        scoreMessage.textContent = 'プロンプトの構造や明確さを改善することで、より良い結果が得られます。';
        circle.style.background = 'linear-gradient(135deg, #f59e0b, #d97706)';
    } else {
        scoreTitle.textContent = '大幅な改善が必要';
        scoreMessage.textContent = 'プロンプトに重要な要素が不足しています。提案を参考に改善してください。';
        circle.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
    }
}

// 構造バッジを表示
function displayStructureBadges(structure) {
    const badges = [
        { key: 'has_role', label: '役割設定' },
        { key: 'has_context', label: 'コンテキスト' },
        { key: 'has_output_format', label: '出力形式' },
        { key: 'has_examples', label: '具体例' },
        { key: 'has_clear_task', label: '明確なタスク' },
    ];

    structureBadges.innerHTML = badges.map(badge => {
        const present = structure[badge.key];
        return `<span class="badge ${present ? 'present' : 'missing'}">
            ${present ? '✓' : '✗'} ${badge.label}
        </span>`;
    }).join('');
}

// 問題を表示
function displayIssues(issues) {
    if (issues.length === 0) {
        issuesSection.style.display = 'none';
        return;
    }

    issuesSection.style.display = 'block';
    issuesList.innerHTML = issues.map(issue => `
        <li>
            <div class="issue-message">${escapeHtml(issue.message)}</div>
            ${issue.suggestion ? `<div class="issue-suggestion">💡 ${escapeHtml(issue.suggestion)}</div>` : ''}
        </li>
    `).join('');
}

// 提案を表示
function displaySuggestions(suggestions) {
    if (suggestions.length === 0) {
        suggestionsSection.style.display = 'none';
        return;
    }

    suggestionsSection.style.display = 'block';
    suggestionsList.innerHTML = suggestions.map(suggestion => `
        <li>
            <div class="suggestion-message">${escapeHtml(suggestion.message)}</div>
            ${suggestion.example ? `<div class="suggestion-example">${escapeHtml(suggestion.example)}</div>` : ''}
        </li>
    `).join('');
}

// HTMLエスケープ
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// コピーボタン
copyBtn.addEventListener('click', async () => {
    const text = optimizedPrompt.textContent;

    try {
        await navigator.clipboard.writeText(text);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'コピーしました!';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    } catch (error) {
        console.error('Copy failed:', error);
        alert('コピーに失敗しました');
    }
});

// Enterキーで分析（Shift+Enterは改行）
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        e.preventDefault();
        analyzeBtn.click();
    }
});
