#!/usr/bin/env python3
"""
Simple HTML-based demo that can be opened in a browser
"""
import os
import glob
import re
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
    
    def search_emails(self, query: str, top_k: int = 3) -> List[Dict]:
        """Simple keyword-based search"""
        query_words = query.lower().split()
        results = []
        
        for email in self.emails_data:
            content_lower = email['content'].lower()
            score = 0
            
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)
            
            if score > 0:
                email_copy = email.copy()
                email_copy['score'] = score
                results.append(email_copy)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

def generate_html_demo():
    """Generate an HTML page with search results for sample queries"""
    
    # Initialize search app
    emails_dir = "/root/Desktop/premier_league_emails_2040"
    search_app = EmailSearchApp(emails_dir)
    
    sample_queries = [
        "Mohamed Salah Jr.の契約条件は？",
        "Gabriel Fernandez 移籍金",
        "Arsenal contract salary",
        "Kai Havertz Jr. transfer"
    ]
    
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚽ プレミアリーグ メール検索システム</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: bold;
        }
        .stats {
            background: #f8f9fa;
            padding: 20px;
            display: flex;
            justify-content: space-around;
            border-bottom: 2px solid #e9ecef;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #11998e;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .content {
            padding: 30px;
        }
        .query-section {
            margin-bottom: 40px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }
        .query-header {
            background: #11998e;
            color: white;
            padding: 15px;
            font-weight: bold;
            font-size: 1.1em;
        }
        .result {
            margin: 20px;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .result-header {
            background: #38ef7d;
            color: white;
            padding: 10px;
            margin: -20px -20px 15px -20px;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        .contract-info {
            background: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #2196f3;
            margin: 10px 0;
        }
        .transfer-info {
            background: #f3e5f5;
            padding: 15px;
            border-left: 4px solid #9c27b0;
            margin: 10px 0;
        }
        .email-details {
            background: #fff3e0;
            padding: 15px;
            border-left: 4px solid #ff9800;
            margin: 10px 0;
            font-family: monospace;
            font-size: 0.9em;
        }
        .no-results {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }
        .footer {
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ プレミアリーグ メール検索システム</h1>
            <p>2040年のプレミアリーグクラブのメールから選手情報を検索</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">""" + str(len(search_app.emails_data)) + """</div>
                <div class="stat-label">総メール数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">3</div>
                <div class="stat-label">対象クラブ</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">Arsenal</div>
                <div class="stat-label">Chelsea</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">Liverpool</div>
                <div class="stat-label">クラブ</div>
            </div>
        </div>
        
        <div class="content">
"""
    
    for query in sample_queries:
        results = search_app.search_emails(query, top_k=2)
        
        html_content += f"""
        <div class="query-section">
            <div class="query-header">
                🔍 質問: {query}
            </div>
"""
        
        if results:
            for i, result in enumerate(results, 1):
                html_content += f"""
            <div class="result">
                <div class="result-header">
                    📧 結果 {i}: {result['club']}/{result['filename']} (スコア: {result['score']})
                </div>
                
                <div class="email-details">
                    <strong>件名:</strong> {result['subject']}<br>
                    <strong>日付:</strong> {result['date']}<br>
                    <strong>送信者:</strong> {result['from']}<br>
                    <strong>宛先:</strong> {result['to']}
                </div>
"""
                
                # Add contract info if found
                if any(word in query.lower() for word in ['契約', 'contract', 'salary']):
                    # Extract contract details
                    salary_match = re.search(r'£([\d,]+)/week|Weekly Wage: £([\d,]+)', result['body'])
                    duration_match = re.search(r'Duration: (\d+) years', result['body'])
                    appearances_match = re.search(r'(\d+) appearances', result['body'])
                    goals_match = re.search(r'(\d+) goals', result['body'])
                    
                    if any([salary_match, duration_match, appearances_match, goals_match]):
                        html_content += '<div class="contract-info"><strong>💼 契約情報:</strong><br>'
                        if salary_match:
                            salary = salary_match.group(1) or salary_match.group(2)
                            html_content += f'💰 週給: £{salary}<br>'
                        if duration_match:
                            html_content += f'📆 契約期間: {duration_match.group(1)}年<br>'
                        if appearances_match:
                            html_content += f'⚽ 出場試合数: {appearances_match.group(1)}試合<br>'
                        if goals_match:
                            html_content += f'🥅 ゴール数: {goals_match.group(1)}ゴール<br>'
                        html_content += '</div>'
                
                # Add transfer info if found
                elif any(word in query.lower() for word in ['移籍', 'transfer']):
                    fee_match = re.search(r'€([\d,]+) million|£([\d,]+) million', result['body'])
                    if fee_match:
                        currency = "€" if fee_match.group(1) else "£"
                        amount = fee_match.group(1) or fee_match.group(2)
                        html_content += f'<div class="transfer-info"><strong>🔄 移籍情報:</strong><br>💵 移籍金: {currency}{amount} million</div>'
                
                html_content += '</div>'
        else:
            html_content += '<div class="no-results">❌ 関連するメールが見つかりませんでした</div>'
        
        html_content += '</div>'
    
    html_content += """
        </div>
        
        <div class="footer">
            🏆 Premier League Email Search System 2040 | Built with Python | 📧 30 emails from Arsenal, Chelsea, Liverpool
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def main():
    print("📄 HTMLデモページを生成中...")
    
    html_content = generate_html_demo()
    
    output_file = "/root/Desktop/premier_league_emails_2040/demo.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ デモページが生成されました: {output_file}")
    print("🌐 ブラウザでファイルを開いて確認できます")
    print("\n📋 含まれているサンプル質問:")
    print("  • Mohamed Salah Jr.の契約条件は？")
    print("  • Gabriel Fernandez 移籍金")
    print("  • Arsenal contract salary") 
    print("  • Kai Havertz Jr. transfer")

if __name__ == "__main__":
    main()