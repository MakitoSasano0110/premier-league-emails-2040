#!/usr/bin/env python3
"""
Interactive HTML page generator for Premier League Email Search
"""
import os
import glob
import re
import json
from typing import List, Dict

class EmailSearchApp:
    def __init__(self, emails_directory: str):
        self.emails_directory = emails_directory
        self.emails_data = []
        self.load_emails()
    
    def load_emails(self):
        """Load all email files and extract content"""
        email_files = glob.glob(os.path.join(self.emails_directory, "**/*.msg"), recursive=True)
        
        for file_path in email_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                email_data = self.parse_email(content, file_path)
                self.emails_data.append(email_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    def parse_email(self, content: str, file_path: str) -> Dict:
        """Parse email content and extract metadata"""
        lines = content.split('\n')
        
        email_data = {
            'file_path': file_path,
            'club': os.path.basename(os.path.dirname(file_path)),
            'filename': os.path.basename(file_path),
            'content': content,
            'from': '',
            'to': '',
            'subject': '',
            'date': '',
            'body': ''
        }
        
        # Extract header information
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith('From:'):
                email_data['from'] = line[5:].strip()
            elif line.startswith('To:'):
                email_data['to'] = line[3:].strip()
            elif line.startswith('Subject:'):
                email_data['subject'] = line[8:].strip()
            elif line.startswith('Date:'):
                email_data['date'] = line[5:].strip()
            elif line.strip() == '' and i > 3:
                body_start = i + 1
                break
        
        email_data['body'] = '\n'.join(lines[body_start:])
        return email_data

def generate_interactive_html():
    """Generate an interactive HTML page with search functionality"""
    
    # Initialize search app and serialize data
    emails_dir = "/root/Desktop/premier_league_emails_2040"
    search_app = EmailSearchApp(emails_dir)
    
    # Convert emails data to JSON for JavaScript
    emails_json = json.dumps(search_app.emails_data, ensure_ascii=False, indent=2)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚽ プレミアリーグ メール検索システム - インタラクティブ版</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 2.5em;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin: 0;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .search-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .search-title {{
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .search-form {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .search-input {{
            flex: 1;
            padding: 15px;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s ease;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }}
        
        .search-button {{
            padding: 15px 30px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .search-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
        }}
        
        .clear-button {{
            padding: 15px 20px;
            background: #95a5a6;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .clear-button:hover {{
            background: #7f8c8d;
        }}
        
        .sample-questions {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }}
        
        .sample-btn {{
            padding: 8px 15px;
            background: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        
        .sample-btn:hover {{
            background: #3498db;
            color: white;
            border-color: #3498db;
        }}
        
        .results-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: none;
        }}
        
        .results-title {{
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .result-item {{
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .result-item:hover {{
            border-color: #3498db;
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.1);
        }}
        
        .result-header {{
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 15px;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .result-content {{
            padding: 20px;
        }}
        
        .email-meta {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
        }}
        
        .contract-info {{
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            margin: 15px 0;
        }}
        
        .transfer-info {{
            background: #fce4ec;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e91e63;
            margin: 15px 0;
        }}
        
        .performance-info {{
            background: #f3e5f5;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #9c27b0;
            margin: 15px 0;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            color: #3498db;
            font-size: 1.1em;
        }}
        
        .footer {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .search-form {{
                flex-direction: column;
            }}
            
            .sample-questions {{
                justify-content: flex-start;
            }}
            
            .stats {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ プレミアリーグ メール検索システム</h1>
            <p>2040年のプレミアリーグクラブのメールから選手情報をリアルタイム検索</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">30</div>
                <div class="stat-label">総メール数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">3</div>
                <div class="stat-label">対象クラブ</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">Arsenal</div>
                <div class="stat-label">アーセナル</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">Chelsea</div>
                <div class="stat-label">チェルシー</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">Liverpool</div>
                <div class="stat-label">リヴァプール</div>
            </div>
        </div>
        
        <div class="search-section">
            <div class="search-title">🔍 質問を入力してください</div>
            <div class="search-form">
                <input type="text" id="searchInput" class="search-input" 
                       placeholder="例: Mohamed Salah Jr.の契約条件は？" 
                       onkeypress="handleKeyPress(event)">
                <button class="search-button" onclick="performSearch()">検索</button>
                <button class="clear-button" onclick="clearResults()">クリア</button>
            </div>
            
            <div class="sample-questions">
                <div class="sample-btn" onclick="fillQuery('Mohamed Salah Jr.の契約条件は？')">
                    Mohamed Salah Jr.の契約
                </div>
                <div class="sample-btn" onclick="fillQuery('Gabriel Fernandez 移籍金')">
                    Gabriel Fernandez移籍金
                </div>
                <div class="sample-btn" onclick="fillQuery('Arsenal contract salary')">
                    Arsenal契約情報
                </div>
                <div class="sample-btn" onclick="fillQuery('Kai Havertz Jr. transfer')">
                    Kai Havertz Jr.移籍
                </div>
                <div class="sample-btn" onclick="fillQuery('Chelsea injury players')">
                    Chelsea怪我選手
                </div>
                <div class="sample-btn" onclick="fillQuery('Liverpool academy player')">
                    Liverpoolアカデミー
                </div>
            </div>
        </div>
        
        <div class="results-section" id="resultsSection">
            <div class="results-title">📋 検索結果</div>
            <div id="resultsContent"></div>
        </div>
        
        <div class="footer">
            🏆 Premier League Email Search System 2040 | 
            Built with JavaScript | 
            📧 Real-time search through Arsenal, Chelsea, Liverpool emails
        </div>
    </div>

    <script>
        // Email data embedded in JavaScript
        const emailsData = {emails_json};
        
        function handleKeyPress(event) {{
            if (event.key === 'Enter') {{
                performSearch();
            }}
        }}
        
        function fillQuery(query) {{
            document.getElementById('searchInput').value = query;
            performSearch();
        }}
        
        function clearResults() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('resultsSection').style.display = 'none';
        }}
        
        function performSearch() {{
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {{
                alert('質問を入力してください');
                return;
            }}
            
            // Show loading
            const resultsSection = document.getElementById('resultsSection');
            const resultsContent = document.getElementById('resultsContent');
            
            resultsSection.style.display = 'block';
            resultsContent.innerHTML = '<div class="loading">🔍 検索中...</div>';
            
            // Simulate search delay for better UX
            setTimeout(() => {{
                const results = searchEmails(query);
                displayResults(query, results);
            }}, 500);
        }}
        
        function searchEmails(query) {{
            const queryWords = query.toLowerCase().split(/\\s+/);
            const results = [];
            
            emailsData.forEach(email => {{
                const contentLower = email.content.toLowerCase();
                let score = 0;
                
                queryWords.forEach(word => {{
                    if (contentLower.includes(word)) {{
                        score += (contentLower.match(new RegExp(word, 'g')) || []).length;
                    }}
                }});
                
                if (score > 0) {{
                    results.push({{
                        ...email,
                        score: score
                    }});
                }}
            }});
            
            // Sort by score and return top 3
            return results.sort((a, b) => b.score - a.score).slice(0, 3);
        }}
        
        function displayResults(query, results) {{
            const resultsContent = document.getElementById('resultsContent');
            
            if (results.length === 0) {{
                resultsContent.innerHTML = `
                    <div class="no-results">
                        ❌ 「${{query}}」に関連するメールが見つかりませんでした。<br>
                        別のキーワードで検索してみてください。
                    </div>
                `;
                return;
            }}
            
            let html = '';
            
            results.forEach((result, index) => {{
                html += `
                    <div class="result-item">
                        <div class="result-header">
                            📧 結果 ${{index + 1}}: ${{result.club}}/${{result.filename}} (スコア: ${{result.score}})
                        </div>
                        <div class="result-content">
                            <div class="email-meta">
                                <strong>📄 件名:</strong> ${{result.subject}}<br>
                                <strong>📅 日付:</strong> ${{result.date}}<br>
                                <strong>👤 送信者:</strong> ${{result.from}}<br>
                                <strong>📧 宛先:</strong> ${{result.to}}
                            </div>
                            ${{extractRelevantInfo(query, result.body)}}
                        </div>
                    </div>
                `;
            }});
            
            resultsContent.innerHTML = html;
        }}
        
        function extractRelevantInfo(query, body) {{
            const queryLower = query.toLowerCase();
            let info = '';
            
            // Check for contract-related queries
            if (queryLower.includes('契約') || queryLower.includes('contract') || queryLower.includes('salary') || queryLower.includes('年俸')) {{
                info += extractContractInfo(body);
            }}
            
            // Check for transfer-related queries
            if (queryLower.includes('移籍') || queryLower.includes('transfer')) {{
                info += extractTransferInfo(body);
            }}
            
            // Check for performance-related queries
            if (queryLower.includes('出場') || queryLower.includes('ゴール') || queryLower.includes('appearances') || queryLower.includes('goals')) {{
                info += extractPerformanceInfo(body);
            }}
            
            // If no specific info found, show general content
            if (!info) {{
                const lines = body.split('\\n').slice(0, 5);
                info = `
                    <div class="performance-info">
                        <strong>📄 内容抜粋:</strong><br>
                        ${{lines.filter(line => line.trim()).map(line => `&nbsp;&nbsp;${{escapeHtml(line.trim())}}`).join('<br>')}}
                    </div>
                `;
            }}
            
            return info;
        }}
        
        function extractContractInfo(body) {{
            let info = '<div class="contract-info"><strong>💼 契約情報:</strong><br>';
            let found = false;
            
            // Extract salary
            const salaryMatch = body.match(/£([\\d,]+)\\/week|Weekly Wage: £([\\d,]+)|Base Salary: £([\\d,]+) per week/);
            if (salaryMatch) {{
                const salary = salaryMatch[1] || salaryMatch[2] || salaryMatch[3];
                info += `💰 週給: £${{salary}}<br>`;
                found = true;
            }}
            
            // Extract contract duration
            const durationMatch = body.match(/Duration: (\\d+) years/);
            if (durationMatch) {{
                info += `📆 契約期間: ${{durationMatch[1]}}年<br>`;
                found = true;
            }}
            
            // Extract appearances
            const appearancesMatch = body.match(/(\\d+) appearances/);
            if (appearancesMatch) {{
                info += `⚽ 出場試合数: ${{appearancesMatch[1]}}試合<br>`;
                found = true;
            }}
            
            // Extract goals
            const goalsMatch = body.match(/(\\d+) goals/);
            if (goalsMatch) {{
                info += `🥅 ゴール数: ${{goalsMatch[1]}}ゴール<br>`;
                found = true;
            }}
            
            // Extract assists
            const assistsMatch = body.match(/(\\d+) assists/);
            if (assistsMatch) {{
                info += `🎯 アシスト数: ${{assistsMatch[1]}}アシスト<br>`;
                found = true;
            }}
            
            info += '</div>';
            return found ? info : '';
        }}
        
        function extractTransferInfo(body) {{
            let info = '<div class="transfer-info"><strong>🔄 移籍情報:</strong><br>';
            let found = false;
            
            // Extract transfer fee
            const feeMatch = body.match(/€([\\d,]+) million|£([\\d,]+) million|Transfer Fee: £([\\d,]+) million/);
            if (feeMatch) {{
                const currency = feeMatch[1] ? '€' : '£';
                const amount = feeMatch[1] || feeMatch[2] || feeMatch[3];
                info += `💵 移籍金: ${{currency}}${{amount}} million<br>`;
                found = true;
            }}
            
            // Extract clubs
            const fromMatch = body.match(/from ([A-Za-z\\s]+)(?:FC|CF)?/);
            if (fromMatch) {{
                info += `🏟️ 移籍元: ${{fromMatch[1].trim()}}<br>`;
                found = true;
            }}
            
            info += '</div>';
            return found ? info : '';
        }}
        
        function extractPerformanceInfo(body) {{
            let info = '<div class="performance-info"><strong>📊 パフォーマンス:</strong><br>';
            let found = false;
            
            // Extract various performance metrics
            const appearances = body.match(/(\\d+) appearances/);
            const goals = body.match(/(\\d+) goals/);
            const assists = body.match(/(\\d+) assists/);
            const cleanSheets = body.match(/(\\d+) clean sheets/);
            
            if (appearances) {{
                info += `⚽ 出場: ${{appearances[1]}}試合<br>`;
                found = true;
            }}
            if (goals) {{
                info += `🥅 ゴール: ${{goals[1]}}ゴール<br>`;
                found = true;
            }}
            if (assists) {{
                info += `🎯 アシスト: ${{assists[1]}}アシスト<br>`;
                found = true;
            }}
            if (cleanSheets) {{
                info += `🛡️ クリーンシート: ${{cleanSheets[1]}}試合<br>`;
                found = true;
            }}
            
            info += '</div>';
            return found ? info : '';
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Initialize with focus on search input
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById('searchInput').focus();
        }});
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    print("🚀 インタラクティブHTMLページを生成中...")
    
    html_content = generate_interactive_html()
    
    output_file = "/root/Desktop/premier_league_emails_2040/interactive_search.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ インタラクティブページが生成されました: {output_file}")
    print("🌐 ブラウザでファイルを開いて、自由に質問を入力できます")
    print("\n📋 機能:")
    print("  • リアルタイム検索")
    print("  • 日本語質問対応")
    print("  • サンプル質問ボタン") 
    print("  • 詳細な契約・移籍情報抽出")
    print("  • レスポンシブデザイン")

if __name__ == "__main__":
    main()