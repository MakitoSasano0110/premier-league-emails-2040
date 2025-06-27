# ⚽ Premier League Email Search System 2040

A RAG (Retrieval-Augmented Generation) based email search system for Premier League clubs. Search through player contracts, transfer information, and performance data from Arsenal, Chelsea, and Liverpool.

## 🌟 Features

- **🔍 Intelligent Search**: Natural language queries in Japanese and English
- **📧 Email Analysis**: 30 emails with contract details, transfer information, and player statistics
- **💼 Contract Information**: Salary details, contract duration, appearance bonuses
- **🔄 Transfer Data**: Transfer fees, club negotiations, player movements
- **📊 Performance Stats**: Goals, assists, appearances, clean sheets
- **🎯 Source Citations**: Every answer includes original email references

## 🏟️ Covered Clubs

- **Arsenal FC** - 10 emails
- **Chelsea FC** - 10 emails  
- **Liverpool FC** - 10 emails

## 🚀 Live Demo

Visit the live application: [Premier League Email Search](https://premier-league-emails-2040.streamlit.app)

## 💡 Sample Queries

Try these example searches:

- `Mohamed Salah Jr.の契約条件は？` - Contract details for Mohamed Salah Jr.
- `Gabriel Fernandez 移籍金` - Transfer fee information
- `Arsenal contract salary` - Arsenal player salaries
- `Kai Havertz Jr. transfer` - Transfer details
- `Chelsea injury players` - Injured players information

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Search**: Keyword-based similarity matching
- **Language**: Python 3.8+
- **Data**: 30 fictional emails from 2040 season

## 📊 Data Overview

The system contains fictional email data including:

- Player contract extensions and negotiations
- Transfer agreements and fees
- Academy player contracts
- Injury reports and insurance claims
- Performance analysis and bonus tracking
- Financial compliance reports

## 🔧 Local Development

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MakitoSasano0110/premier-league-emails-2040.git
cd premier-league-emails-2040
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
premier-league-emails-2040/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── Arsenal/                  # Arsenal FC emails (10 files)
├── Chelsea/                  # Chelsea FC emails (10 files)
├── Liverpool/               # Liverpool FC emails (10 files)
└── .gitignore               # Git ignore file
```

## 🎯 Key Features

### Smart Information Extraction

The system automatically extracts and formats:

- **💰 Salary Information**: Weekly wages, bonuses, contract terms
- **📅 Contract Details**: Duration, extension options, performance clauses
- **⚽ Performance Data**: Goals, assists, appearances, clean sheets
- **🔄 Transfer Information**: Fees, add-ons, payment schedules
- **🏥 Medical Information**: Injury reports, recovery timelines

### Multi-language Support

- Japanese queries: `Mohamed Salah Jr.の契約条件は？`
- English queries: `Arsenal contract salary`
- Mixed language support for international users

## 📈 Future Enhancements

- [ ] Advanced semantic search with embeddings
- [ ] More Premier League clubs
- [ ] Historical data integration
- [ ] Advanced analytics and visualizations
- [ ] Real-time data updates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**Note**: This is a demonstration project using fictional data for educational purposes. All player names, contracts, and financial information are purely fictional and not related to real Premier League data.