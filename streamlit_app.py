import streamlit as st
import os
import glob
import re
from typing import List, Dict

# Configure page
st.set_page_config(
    page_title="⚽ Premier League Email Search",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

class EmailSearchApp:
    def __init__(self, emails_directory: str = "."):
        self.emails_directory = emails_directory
        self.emails_data = self.load_emails()
    
    @st.cache_data
    def load_emails(_self):
        """Load all email files and extract content"""
        emails_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Search for email files in subdirectories
        email_files = []
        for club in ["Arsenal", "Chelsea", "Liverpool"]:
            club_dir = os.path.join(_self.emails_directory, club)
            if os.path.exists(club_dir):
                email_files.extend(glob.glob(os.path.join(club_dir, "*.msg")))
        
        total_files = len(email_files)
        for i, file_path in enumerate(email_files):
            try:
                progress = (i + 1) / total_files
                progress_bar.progress(progress)
                status_text.text(f"Loading {os.path.basename(file_path)}... ({i+1}/{total_files})")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                email_data = _self.parse_email_static(content, file_path)
                emails_data.append(email_data)
            except Exception as e:
                st.error(f"Error loading {file_path}: {e}")
        
        progress_bar.empty()
        status_text.empty()
        
        return emails_data
    
    @staticmethod
    def parse_email_static(content: str, file_path: str) -> Dict:
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
    
    def generate_answer(self, query: str, search_results: List[Dict]) -> tuple[str, str]:
        """Generate direct answer and sources based on search results"""
        if not search_results:
            return "申し訳ございませんが、関連するメールが見つかりませんでした。", ""
        
        # Generate direct answer first
        direct_answer = self.generate_direct_answer(query, search_results)
        
        # Generate sources section
        sources = "\n## 📋 参考となったメール\n\n"
        
        for i, result in enumerate(search_results, 1):
            sources += f"**{i}. {result['club']} - {result['subject']}**\n"
            sources += f"📅 {result['date']} | 📧 {result['filename']}\n"
            
            # Show relevant excerpt
            lines = result['body'].split('\n')[:3]
            sources += "💬 内容抜粋: "
            excerpt = ""
            for line in lines:
                if line.strip():
                    excerpt += line.strip() + " "
                    if len(excerpt) > 100:
                        excerpt = excerpt[:100] + "..."
                        break
            sources += excerpt + "\n\n"
        
        return direct_answer, sources
    
    def generate_direct_answer(self, query: str, search_results: List[Dict]) -> str:
        """Generate a direct, concise answer to the user's question"""
        if not search_results:
            return "関連情報が見つかりませんでした。"
        
        # Analyze query type and generate appropriate answer
        query_lower = query.lower()
        
        # Contract/Salary related questions
        if any(word in query_lower for word in ['契約', '年俸', 'salary', 'contract', '週給']):
            return self.answer_contract_question(query, search_results)
        
        # Transfer related questions
        elif any(word in query_lower for word in ['移籍', 'transfer', '移籍金', 'fee']):
            return self.answer_transfer_question(query, search_results)
        
        # Player performance questions
        elif any(word in query_lower for word in ['ゴール', 'goals', 'アシスト', 'assists', '出場', 'appearances']):
            return self.answer_performance_question(query, search_results)
        
        # General questions
        else:
            return self.answer_general_question(query, search_results)
    
    def answer_contract_question(self, query: str, search_results: List[Dict]) -> str:
        """Answer contract-related questions"""
        for result in search_results:
            contract_info = self.extract_contract_info(result['body'])
            if contract_info:
                # Extract key information for direct answer
                body = result['body']
                player_name = self.extract_player_name(query, result)
                
                # Extract salary
                salary_match = re.search(r'£([\d,]+)/week|Weekly Wage: £([\d,]+)|Base Salary: £([\d,]+)', body)
                if salary_match:
                    salary = salary_match.group(1) or salary_match.group(2) or salary_match.group(3)
                    return f"💰 **{player_name}の契約条件:** 週給£{salary}です。"
                
                # Extract duration
                duration_match = re.search(r'Duration: (\d+) years', body)
                if duration_match:
                    duration = duration_match.group(1)
                    return f"📅 **{player_name}の契約期間:** {duration}年契約です。"
        
        return "💼 契約に関する具体的な情報が見つかりませんでした。"
    
    def answer_transfer_question(self, query: str, search_results: List[Dict]) -> str:
        """Answer transfer-related questions"""
        for result in search_results:
            body = result['body']
            player_name = self.extract_player_name(query, result)
            
            # Extract transfer fee
            fee_patterns = [
                r'Transfer Fee: £([\d,]+) million',
                r'Fee: £([\d,]+) million',
                r'€([\d,]+) million'
            ]
            
            for pattern in fee_patterns:
                match = re.search(pattern, body)
                if match:
                    fee = match.group(1)
                    currency = "£" if "£" in pattern else "€"
                    return f"💵 **{player_name}の移籍金:** {currency}{fee} millionです。"
        
        return "🔄 移籍金に関する具体的な情報が見つかりませんでした。"
    
    def answer_performance_question(self, query: str, search_results: List[Dict]) -> str:
        """Answer performance-related questions"""
        for result in search_results:
            body = result['body']
            player_name = self.extract_player_name(query, result)
            
            stats = []
            
            # Extract goals
            goals_match = re.search(r'(\d+) goals', body)
            if goals_match:
                stats.append(f"{goals_match.group(1)}ゴール")
            
            # Extract assists
            assists_match = re.search(r'(\d+) assists', body)
            if assists_match:
                stats.append(f"{assists_match.group(1)}アシスト")
            
            # Extract appearances
            appearances_match = re.search(r'(\d+) appearances', body)
            if appearances_match:
                stats.append(f"{appearances_match.group(1)}試合出場")
            
            if stats:
                return f"⚽ **{player_name}の成績:** {', '.join(stats)}です。"
        
        return "📊 成績に関する具体的な情報が見つかりませんでした。"
    
    def answer_general_question(self, query: str, search_results: List[Dict]) -> str:
        """Answer general questions"""
        result = search_results[0]  # Use the most relevant result
        player_name = self.extract_player_name(query, result)
        
        # Extract first meaningful sentence from email body
        lines = result['body'].split('\n')
        for line in lines:
            if line.strip() and len(line.strip()) > 20:
                return f"📧 **{player_name}について:** {line.strip()[:150]}..."
        
        return f"📄 {result['club']}からの{player_name}に関する情報が見つかりました。"
    
    def extract_player_name(self, query: str, result: Dict) -> str:
        """Extract player name from query or email content"""
        # Try to extract name from query
        words = query.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Potential name found
                name_parts = [word]
                # Check next words for more name parts
                for j in range(i+1, min(i+3, len(words))):
                    if words[j][0].isupper() or words[j].endswith('.'):
                        name_parts.append(words[j])
                    else:
                        break
                if len(name_parts) >= 1:
                    return ' '.join(name_parts)
        
        # Fallback to extracting from email subject or content
        subject = result.get('subject', '')
        if 'Contract' in subject or 'Transfer' in subject:
            # Extract name from subject
            subject_words = subject.split()
            for word in subject_words:
                if word[0].isupper() and len(word) > 2 and word not in ['Contract', 'Transfer', 'Update', 'News']:
                    return word
        
        return "選手"
    
    def extract_contract_info(self, body: str) -> str:
        """Extract contract-related information"""
        info = "💼 契約情報:\n"
        found_info = False
        
        # Extract salary information
        salary_patterns = [
            r'£([\d,]+)/week',
            r'Weekly Wage: £([\d,]+)',
            r'Base Salary: £([\d,]+) per week'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, body)
            if match:
                info += f"  💰 週給: £{match.group(1)}\n"
                found_info = True
                break
        
        # Extract contract duration
        duration_match = re.search(r'Duration: (\d+) years', body)
        if duration_match:
            info += f"  📆 契約期間: {duration_match.group(1)}年\n"
            found_info = True
        
        # Extract appearances
        appearances_match = re.search(r'(\d+) appearances', body)
        if appearances_match:
            info += f"  ⚽ 出場試合数: {appearances_match.group(1)}試合\n"
            found_info = True
        
        # Extract goals
        goals_match = re.search(r'(\d+) goals', body)
        if goals_match:
            info += f"  🥅 ゴール数: {goals_match.group(1)}ゴール\n"
            found_info = True
        
        # Extract assists
        assists_match = re.search(r'(\d+) assists', body)
        if assists_match:
            info += f"  🎯 アシスト数: {assists_match.group(1)}アシスト\n"
            found_info = True
        
        return info if found_info else ""
    
    def extract_transfer_info(self, body: str) -> str:
        """Extract transfer-related information"""
        info = "🔄 移籍情報:\n"
        found_info = False
        
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
                info += f"  💵 移籍金: {currency}{match.group(1)} million\n"
                found_info = True
                break
        
        return info if found_info else ""

@st.cache_resource
def get_email_search_app():
    """Create and cache the EmailSearchApp instance"""
    return EmailSearchApp()

def main():
    # Header
    st.title("⚽ プレミアリーグ メール検索システム")
    st.markdown("### 2040年のプレミアリーグクラブのメールから選手情報を検索")
    
    # Initialize the app with caching
    with st.spinner("📧 メールデータを読み込み中..."):
        search_app = get_email_search_app()
    st.success(f"✅ {len(search_app.emails_data)}通のメールを読み込みました")
    
    # Sidebar with information
    with st.sidebar:
        st.header("📊 システム情報")
        total_emails = len(search_app.emails_data)
        clubs = list(set([email['club'] for email in search_app.emails_data]))
        
        st.metric("📧 総メール数", total_emails)
        st.metric("🏟️ 対象クラブ数", len(clubs))
        
        st.subheader("🏆 対象クラブ")
        for club in sorted(clubs):
            club_emails = len([e for e in search_app.emails_data if e['club'] == club])
            st.write(f"🔸 **{club}**: {club_emails}通")
        
        st.markdown("---")
        st.subheader("💡 使い方のヒント")
        st.markdown("""
        - 選手名は英語で入力
        - 質問は日本語OK
        - 「契約」「移籍」「年俸」などのキーワードを使用
        """)
    
    # Sample questions
    st.subheader("🔍 サンプル質問")
    sample_questions = [
        "Mohamed Salah Jr.の契約条件は？",
        "Gabriel Fernandez 移籍金",
        "Arsenal contract salary", 
        "Chelsea transfer fee",
        "Kai Havertz Jr. transfer"
    ]
    
    cols = st.columns(len(sample_questions))
    for i, question in enumerate(sample_questions):
        if cols[i].button(f"📝 {question}", key=f"sample_{i}"):
            st.session_state.query_input = question
    
    # Main search interface
    st.markdown("---")
    st.subheader("💬 質問を入力してください")
    
    # Text input
    query = st.text_input(
        "質問:",
        value=st.session_state.get('query_input', ''),
        placeholder="例: Mohamed Salah Jr.の契約内容を教えて",
        key="main_query"
    )
    
    # Clear the sample question from session state
    if 'query_input' in st.session_state:
        del st.session_state.query_input
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 4])
    search_clicked = col1.button("🔍 検索", type="primary")
    clear_clicked = col2.button("🗑️ クリア")
    
    if clear_clicked:
        st.rerun()
    
    # Perform search
    if search_clicked and query:
        with st.spinner("🔍 検索中..."):
            results = search_app.search_emails(query, top_k=3)
            
            if results:
                st.success(f"✅ {len(results)}件の関連メールが見つかりました")
                
                # Generate direct answer and sources
                direct_answer, sources = search_app.generate_answer(query, results)
                
                st.markdown("---")
                st.subheader("💡 回答")
                st.markdown(direct_answer)
                
                st.markdown(sources)
                
                # Show detailed email content in expandable sections
                st.markdown("---")
                st.subheader("📧 詳細なメール内容")
                
                for i, result in enumerate(results, 1):
                    with st.expander(f"📄 {i}. {result['club']} - {result['subject']} (スコア: {result['score']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**送信者:** {result['from']}")
                            st.write(f"**宛先:** {result['to']}")
                        
                        with col2:
                            st.write(f"**日付:** {result['date']}")
                            st.write(f"**クラブ:** {result['club']}")
                        
                        st.markdown("**内容:**")
                        st.text(result['body'])
            else:
                st.warning("❌ 関連するメールが見つかりませんでした。別のキーワードで検索してみてください。")
    
    elif search_clicked and not query:
        st.error("⚠️ 質問を入力してください")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    🏆 Premier League Email Search System 2040 | 
    Built with Streamlit | 
    📧 30 emails from Arsenal, Chelsea, Liverpool
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()