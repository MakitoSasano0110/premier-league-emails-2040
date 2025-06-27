#!/usr/bin/env python3
"""
Test demo of the Premier League Email RAG Chatbot
"""
import os
import glob
import re
from typing import List, Dict

class SimpleEmailSearch:
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
    
    def simple_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Simple keyword-based search"""
        query_words = query.lower().split()
        results = []
        
        for email in self.emails_data:
            content_lower = email['content'].lower()
            score = 0
            
            # Simple scoring based on keyword matches
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)
            
            if score > 0:
                email_copy = email.copy()
                email_copy['score'] = score
                results.append(email_copy)
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, query: str, search_results: List[Dict]) -> str:
        """Generate answer based on search results"""
        if not search_results:
            return "申し訳ございませんが、関連するメールが見つかりませんでした。"
        
        answer = f"質問: {query}\n検索結果：\n\n"
        
        for i, result in enumerate(search_results, 1):
            answer += f"**{i}. 出典: {result['club']}/{result['filename']} (スコア: {result['score']})**\n"
            answer += f"件名: {result['subject']}\n"
            answer += f"日付: {result['date']}\n"
            
            # Extract relevant information based on query
            if any(word in query.lower() for word in ['契約', '年俸', 'salary', 'contract']):
                answer += self.extract_contract_info(result['body'])
            elif any(word in query.lower() for word in ['移籍', 'transfer']):
                answer += self.extract_transfer_info(result['body'])
            else:
                # Show first few lines of content
                lines = result['body'].split('\n')[:5]
                answer += "内容抜粋:\n"
                for line in lines:
                    if line.strip():
                        answer += f"  {line.strip()}\n"
            
            answer += "\n" + "="*50 + "\n\n"
        
        return answer
    
    def extract_contract_info(self, body: str) -> str:
        """Extract contract-related information"""
        info = "契約情報:\n"
        
        # Extract salary information
        salary_patterns = [
            r'£([\d,]+)/week',
            r'Weekly Wage: £([\d,]+)',
            r'Base Salary: £([\d,]+) per week'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, body)
            if match:
                info += f"  週給: £{match.group(1)}\n"
                break
        
        # Extract contract duration
        duration_match = re.search(r'Duration: (\d+) years', body)
        if duration_match:
            info += f"  契約期間: {duration_match.group(1)}年\n"
        
        # Extract bonuses
        bonus_matches = re.findall(r'£([\d,]+) per', body)
        if bonus_matches:
            info += f"  ボーナス: £{', £'.join(bonus_matches)}\n"
        
        # Extract appearances
        appearances_match = re.search(r'(\d+) appearances', body)
        if appearances_match:
            info += f"  出場試合数: {appearances_match.group(1)}試合\n"
        
        # Extract goals
        goals_match = re.search(r'(\d+) goals', body)
        if goals_match:
            info += f"  ゴール数: {goals_match.group(1)}ゴール\n"
        
        return info
    
    def extract_transfer_info(self, body: str) -> str:
        """Extract transfer-related information"""
        info = "移籍情報:\n"
        
        # Extract transfer fee
        fee_patterns = [
            r'Transfer Fee: £([\d,]+) million',
            r'Fee: £([\d,]+) million',
            r'€([\d,]+) million'
        ]
        
        for pattern in fee_patterns:
            match = re.search(pattern, body)
            if match:
                currency = "£" if "£" in pattern else "€"
                info += f"  移籍金: {currency}{match.group(1)} million\n"
                break
        
        return info

def test_queries():
    """Test the search functionality with sample queries"""
    
    print("🏁 プレミアリーグ メール検索システム テスト")
    print("="*60)
    
    # Initialize search engine
    emails_dir = "/root/Desktop/premier_league_emails_2040"
    search_engine = SimpleEmailSearch(emails_dir)
    
    print(f"📧 {len(search_engine.emails_data)}通のメールを読み込みました")
    print()
    
    # Test queries
    test_queries_list = [
        "Mohamed Salah Jr.の契約条件は？",
        "Gabriel Fernandez 移籍金",
        "Arsenal contract salary",
        "Chelsea transfer fee",
        "Liverpool academy player"
    ]
    
    for query in test_queries_list:
        print(f"🔍 テスト質問: {query}")
        print("-" * 40)
        
        results = search_engine.simple_search(query, top_k=2)
        
        if results:
            answer = search_engine.generate_answer(query, results)
            print(answer)
        else:
            print("❌ 関連するメールが見つかりませんでした\n")
        
        print("\n" + "🔸" * 60 + "\n")

if __name__ == "__main__":
    test_queries()