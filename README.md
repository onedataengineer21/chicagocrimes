# Chicago Crimes Analytics Dashboard

Interactive Streamlit dashboard for analyzing Chicago crime data with daily, weekly, and monthly views.

## Features

- 📊 **Interactive KPIs**: Total crimes, arrest rate, domestic crimes, top crime types
- 📈 **Time Series Analysis**: View crime patterns by hour, day, or date
- 🗺️ **Geographic Heatmap**: Crime density visualization across Chicago
- 🎯 **Crime Distribution**: Analyze crime types and locations
- 👮 **Arrest Analysis**: Compare total crimes vs arrests by type
- ⏰ **24-Hour Pattern**: Understand when crimes occur throughout the day

## Tech Stack

- **Python 3.9+**
- **Streamlit** - Interactive web framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations

## Setup

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get the data**:
   - Download the Chicago Crimes dataset from [Chicago Data Portal](https://data.cityofchicago.org/Public-Safety/Crimes-One-year-prior-to-present/x2n5-8w5q)
   - Save as `chicagocrimes.csv` in this directory

3. **Run the dashboard**:
   ```bash
   streamlit run chicago_crimes_dashboard.py
   ```

### Streamlit Cloud Deployment

For Streamlit Cloud deployment, you'll need to upload the CSV file separately or modify the app to fetch data from a URL.

## Data Requirements

The dashboard expects a CSV file with the following columns:
- `DATE OF OCCURRENCE` - Date and time of the crime
- `PRIMARY DESCRIPTION` - Type of crime
- `SECONDARY DESCRIPTION` - Crime subtype
- `LOCATION DESCRIPTION` - Where the crime occurred
- `ARREST` - Y/N indicator
- `DOMESTIC` - Y/N indicator
- `LATITUDE` - Geographic coordinate
- `LONGITUDE` - Geographic coordinate
- `WARD` - Chicago ward number
- `BEAT` - Police beat number

## Color Theme

- **Primary**: Oxford Blue (#002147)
- **Secondary**: Selective Yellow (#FFBA00)

## License

MIT

---

🤖 Built with [Claude Code](https://claude.com/claude-code)
