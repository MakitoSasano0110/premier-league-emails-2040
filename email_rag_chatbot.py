import streamlit as st
import os
import glob
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import re

class EmailRAGChatbot:
    def __init__(self, emails_directory: str):
        self.emails_directory = emails_directory
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.emails_data = []
        self.index = None
        self.load_emails()
        self.create_index()
    
    def load_emails(self):
        """Load all email files and extract content"""
        email_files = glob.glob(os.path.join(self.emails_directory, "**/*.msg"), recursive=True)
        
        for file_path in email_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract email metadata
                email_data = self.parse_email(content, file_path)
                self.emails_data.append(email_data)
            except Exception as e:
                st.error(f"Error loading {file_path}: {e}")
    
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
            elif line.strip() == '' and i > 3:  # Empty line after headers
                body_start = i + 1
                break
        
        # Extract body
        email_data['body'] = '\n'.join(lines[body_start:])
        
        return email_data
    
    def create_index(self):
        """Create FAISS index for semantic search"""
        if not self.emails_data:
            return
        
        # Create embeddings for email content
        texts = [email['content'] for email in self.emails_data]
        embeddings = self.model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
    
    def search_emails(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant emails based on query"""
        if not self.index:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.emails_data):
                email = self.emails_data[idx].copy()
                email['similarity_score'] = float(score)
                results.append(email)
        
        return results
    
    def generate_answer(self, query: str, search_results: List[Dict]) -> str:
        """Generate answer based on search results"""
        if not search_results:
            return "申し訳ございませんが、関連するメールが見つかりませんでした。"
        
        # Extract relevant information from search results
        relevant_info = []
        sources = []
        
        for result in search_results:
            club = result['club']
            subject = result['subject']
            body = result['body']
            filename = result['filename']
            
            relevant_info.append(f"【{club}】{subject}\n{body}")
            sources.append(f"{club}/{filename}")
        
        # Generate contextual answer based on query type
        answer = self.create_contextual_answer(query, relevant_info, sources)
        
        return answer
    
    def create_contextual_answer(self, query: str, relevant_info: List[str], sources: List[str]) -> str:
        """Create contextual answer based on query and email content"""
        query_lower = query.lower()
        
        # Analyze query intent
        if any(word in query_lower for word in ['契約', '年俸', '給与', 'salary', 'contract']):
            return self.answer_contract_query(query, relevant_info, sources)
        elif any(word in query_lower for word in ['移籍', 'transfer', '移籍金']):
            return self.answer_transfer_query(query, relevant_info, sources)
        elif any(word in query_lower for word in ['出場', 'appearances', '試合', 'matches']):
            return self.answer_performance_query(query, relevant_info, sources)
        elif any(word in query_lower for word in ['怪我', 'injury', '負傷']):
            return self.answer_injury_query(query, relevant_info, sources)
        else:
            return self.answer_general_query(query, relevant_info, sources)
    
    def answer_contract_query(self, query: str, relevant_info: List[str], sources: List[str]) -> str:
        """Answer contract-related queries"""
        answer = "契約に関する情報：\n\n"
        
        for i, info in enumerate(relevant_info):
            # Extract contract details
            salary_match = re.search(r'£([\d,]+)/week|£([\d,]+) per week|Weekly Wage: £([\d,]+)', info)
            contract_match = re.search(r'Duration: (\d+) years|Contract: (\d+) years', info)
            bonus_matches = re.findall(r'Bonus: £([\d,]+)', info)
            
            answer += f"**出典: {sources[i]}**\n"
            
            if salary_match:
                salary = salary_match.group(1) or salary_match.group(2) or salary_match.group(3)
                answer += f"- 週給: £{salary}\n"
            
            if contract_match:
                duration = contract_match.group(1) or contract_match.group(2)
                answer += f"- 契約期間: {duration}年\n"
            
            if bonus_matches:
                answer += f"- ボーナス: " + ", ".join([f"£{bonus}" for bonus in bonus_matches]) + "\n"
            
            answer += "\n"
        
        return answer
    
    def answer_transfer_query(self, query: str, relevant_info: List[str], sources: List[str]) -> str:
        """Answer transfer-related queries"""
        answer = "移籍に関する情報：\n\n"
        
        for i, info in enumerate(relevant_info):
            # Extract transfer details
            fee_match = re.search(r'Transfer Fee: £([\d,]+) million|Fee: £([\d,]+) million|€([\d,]+) million', info)
            from_club_match = re.search(r'from ([A-Za-z\s]+)', info)
            
            answer += f"**出典: {sources[i]}**\n"
            
            if fee_match:
                fee = fee_match.group(1) or fee_match.group(2) or fee_match.group(3)
                currency = "£" if fee_match.group(1) or fee_match.group(2) else "€"
                answer += f"- 移籍金: {currency}{fee} million\n"
            
            if from_club_match:
                from_club = from_club_match.group(1).strip()
                answer += f"- 移籍元: {from_club}\n"
            
            answer += "\n"
        
        return answer
    
    def answer_performance_query(self, query: str, relevant_info: List[str], sources: List[str]) -> str:
        """Answer performance-related queries"""
        answer = "パフォーマンス統計：\n\n"
        
        for i, info in enumerate(relevant_info):
            # Extract performance stats
            appearances_match = re.search(r'(\d+) appearances', info)
            goals_match = re.search(r'(\d+) goals', info)
            assists_match = re.search(r'(\d+) assists', info)
            
            answer += f"**出典: {sources[i]}**\n"
            
            if appearances_match:
                appearances = appearances_match.group(1)
                answer += f"- 出場試合数: {appearances}試合\n"
            
            if goals_match:
                goals = goals_match.group(1)
                answer += f"- ゴール数: {goals}ゴール\n"
            
            if assists_match:
                assists = assists_match.group(1)
                answer += f"- アシスト数: {assists}アシスト\n"
            
            answer += "\n"
        
        return answer
    
    def answer_injury_query(self, query: str, relevant_info: List[str], sources: List[str]) -> str:
        """Answer injury-related queries"""
        answer = "怪我・負傷に関する情報：\n\n"
        
        for i, info in enumerate(relevant_info):
            answer += f"**出典: {sources[i]}**\n"
            
            # Extract injury information
            if 'injury' in info.lower() or '怪我' in info:
                injury_lines = [line for line in info.split('\n') if 'injury' in line.lower() or 'injured' in line.lower()]
                for line in injury_lines:
                    answer += f"- {line.strip()}\n"
            
            answer += "\n"
        
        return answer
    
    def answer_general_query(self, query: str, relevant_info: List[str], sources: List[str]) -> str:
        """Answer general queries"""
        answer = "関連情報：\n\n"
        
        for i, info in enumerate(relevant_info):
            answer += f"**出典: {sources[i]}**\n"
            # Take first few lines of the email body
            lines = info.split('\n')
            body_lines = [line for line in lines if line.strip() and not line.startswith('【')]
            answer += '\n'.join(body_lines[:5]) + "\n\n"
        
        return answer

def main():
    st.set_page_config(
        page_title="プレミアリーグ メール検索チャットボット",
        page_icon="⚽",
        layout="wide"
    )
    
    st.title("⚽ プレミアリーグ メール検索チャットボット")
    st.markdown("2040年のプレミアリーグクラブのメールから選手の契約情報を検索できます")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner("メールデータを読み込み中..."):
            emails_dir = "/root/Desktop/premier_league_emails_2040"
            st.session_state.chatbot = EmailRAGChatbot(emails_dir)
            st.success(f"{len(st.session_state.chatbot.emails_data)}通のメールを読み込みました")
    
    # Chat interface
    st.subheader("質問を入力してください")
    
    # Sample questions
    with st.expander("サンプル質問"):
        st.markdown("""
        - Mohamed Salah Jr.の契約条件は？
        - Arsenalの選手の年俸はいくら？
        - Gabriel Fernandezの移籍金は？
        - 怪我をしている選手は誰？
        - Chelsea academy出身の選手は？
        """)
    
    user_query = st.text_input("質問:", placeholder="例: Mohamed Salah Jr.の契約内容を教えて")
    
    if user_query:
        with st.spinner("検索中..."):
            # Search for relevant emails
            search_results = st.session_state.chatbot.search_emails(user_query, top_k=3)
            
            if search_results:
                # Generate answer
                answer = st.session_state.chatbot.generate_answer(user_query, search_results)
                
                # Display answer
                st.subheader("回答")
                st.markdown(answer)
                
                # Display source emails
                st.subheader("参照したメール")
                for result in search_results:
                    with st.expander(f"{result['club']} - {result['subject']} (類似度: {result['similarity_score']:.3f})"):
                        st.text(f"送信者: {result['from']}")
                        st.text(f"宛先: {result['to']}")
                        st.text(f"日付: {result['date']}")
                        st.text(f"件名: {result['subject']}")
                        st.text("内容:")
                        st.text(result['body'])
            else:
                st.warning("関連するメールが見つかりませんでした。")
    
    # Statistics
    with st.sidebar:
        st.subheader("統計情報")
        if 'chatbot' in st.session_state:
            total_emails = len(st.session_state.chatbot.emails_data)
            clubs = list(set([email['club'] for email in st.session_state.chatbot.emails_data]))
            
            st.metric("総メール数", total_emails)
            st.metric("クラブ数", len(clubs))
            
            st.subheader("対象クラブ")
            for club in sorted(clubs):
                club_emails = len([e for e in st.session_state.chatbot.emails_data if e['club'] == club])
                st.text(f"{club}: {club_emails}通")

if __name__ == "__main__":
    main()