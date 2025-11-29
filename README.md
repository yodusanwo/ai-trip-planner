# ✈️ AI Trip Planner

An intelligent trip planning application powered by CrewAI and Streamlit. Plan your perfect trip with AI agents that research destinations, review recommendations, and create beautiful day-by-day itineraries.

## 🌟 Features

- **🤖 Multi-Agent AI System**: Three specialized AI agents work together
  - **Trip Researcher**: Finds attractions, restaurants, and activities
  - **Trip Reviewer**: Analyzes and prioritizes recommendations
  - **Trip Planner**: Creates detailed HTML itineraries

- **⚡ Optimized Performance**: 
  - Uses GPT-4o-mini for speed (45s - 2.5min execution)
  - Dynamic time estimates based on trip complexity
  - Configurable agent iterations and rate limits

- **🎨 Beautiful Interface**:
  - Modern Streamlit web UI
  - Real-time progress tracking
  - Dynamic agent status updates
  - Responsive design

- **📄 Professional Output**:
  - Styled HTML itineraries
  - Day-by-day schedules with times and costs
  - Budget breakdowns
  - Downloadable trip plans

- **🔒 Security Features** (New!):
  - Rate limiting (5 trips/hour, 20 trips/day)
  - Input validation & sanitization
  - Daily cost cap ($10/day default)
  - Real-time usage statistics

## 🚀 Quick Start

### Prerequisites

- Python 3.10-3.13
- OpenAI API key
- Serper API key (for web search)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Zora-Digital/trip_planner.git
cd trip_planner
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
# or
uv sync
```

3. **Set up environment variables:**

Create a `.env` file:
```env
OPENAI_API_KEY=your-openai-api-key
SERPER_API_KEY=your-serper-api-key
MODEL=gpt-4o-mini
```

4. **Run the Streamlit app:**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage

1. **Enter trip details:**
   - Destination (e.g., "Paris, France")
   - Duration (e.g., "5 days")
   - Budget level (Budget/Mid-Range/Luxury)
   - Travel style preferences
   - Special requirements

2. **Click "Plan My Trip"**

3. **Watch the AI agents work:**
   - Real-time progress updates
   - Agent status indicators
   - Time estimates

4. **Get your itinerary:**
   - Beautiful HTML format
   - Download for offline use
   - Print to PDF from browser

## 🔒 Security

This application includes built-in security features:

- **Rate Limiting**: Prevents abuse (5 trips/hour, 20/day)
- **Input Validation**: Blocks malicious inputs
- **Cost Cap**: Protects your budget ($10/day default)
- **Usage Dashboard**: Monitor your usage in real-time

See [SECURITY.md](SECURITY.md) for detailed documentation.

## ⚙️ Configuration

### Adjust Security Settings

Edit the configuration at the top of `app.py`:

```python
MAX_TRIPS_PER_HOUR = 5
MAX_TRIPS_PER_DAY = 20
DAILY_COST_CAP_USD = 10.0
```

### Change AI Model

Edit `.env`:
```env
MODEL=gpt-4o-mini  # Fast & cheap
# MODEL=gpt-4o     # Higher quality
```

### Optimize Performance

Edit `src/trip_planner/crew.py`:
```python
max_iter=5    # Fewer iterations = faster
max_rpm=30    # Higher RPM = faster API calls
```

## 🚢 Deployment

### Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Set main file: `app.py`
5. Add secrets in dashboard
6. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📊 Performance

| Trip Duration | Estimated Time | Cost (gpt-4o-mini) |
|--------------|----------------|-------------------|
| 1-2 days | 45-75 seconds | $0.01-0.02 |
| 3-4 days | 60-90 seconds | $0.02-0.03 |
| 5-7 days | 1.5-2 minutes | $0.03-0.04 |
| 8+ days | 2-2.5 minutes | $0.04-0.05 |

## 🏗️ Project Structure

```
trip_planner/
├── app.py                          # Streamlit frontend
├── security_config.py              # Security settings
├── src/trip_planner/
│   ├── crew.py                     # CrewAI configuration
│   ├── config/
│   │   ├── agents.yaml            # Agent definitions
│   │   └── tasks.yaml             # Task definitions
│   └── tools/
│       └── custom_tool.py         # Custom tools
├── .streamlit/
│   ├── config.toml                # Streamlit config
│   └── secrets.toml.example       # Secrets template
├── output/                         # Generated trip plans
├── requirements.txt               # Python dependencies
├── SECURITY.md                    # Security documentation
└── DEPLOYMENT.md                  # Deployment guide
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [CrewAI](https://crewai.com)
- Frontend powered by [Streamlit](https://streamlit.io)
- AI by [OpenAI](https://openai.com)
- Search by [Serper](https://serper.dev)

## 📞 Support

- 📚 [Documentation](DEPLOYMENT.md)
- 🔒 [Security Guide](SECURITY.md)
- 🐛 [Report Issues](https://github.com/Zora-Digital/trip_planner/issues)
- 💬 [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)

---

**Made with ❤️ using CrewAI and Streamlit**
