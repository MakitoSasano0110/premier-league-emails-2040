#!/usr/bin/env python3
"""
Test specific query about Kai Havertz Jr.
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
    
    def simple_search(self, query: str, top_k: int = 5) -> List[Dict]:
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

def search_kai_havertz():
    """Search for information about Kai Havertz Jr."""
    
    print("🔍 Kai Havertz Jr.に関する情報を検索中...")
    print("="*60)
    
    # Initialize search engine
    emails_dir = "/root/Desktop/premier_league_emails_2040"
    search_engine = SimpleEmailSearch(emails_dir)
    
    # Search for Kai Havertz Jr.
    query = "Kai Havertz Jr"
    results = search_engine.simple_search(query, top_k=3)
    
    if results:
        print(f"📧 {len(results)}件の関連メールが見つかりました\n")
        
        for i, result in enumerate(results, 1):
            print(f"**{i}. 出典: {result['club']}/{result['filename']} (スコア: {result['score']})**")
            print(f"件名: {result['subject']}")
            print(f"日付: {result['date']}")
            print(f"送信者: {result['from']}")
            print(f"宛先: {result['to']}")
            print("\n内容:")
            
            # Show relevant parts of the email
            lines = result['body'].split('\n')
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            
            print("\n" + "="*60 + "\n")
    else:
        print("❌ Kai Havertz Jr.に関するメールが見つかりませんでした")

if __name__ == "__main__":
    search_kai_havertz()