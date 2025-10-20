# 🛰️ EOPF Copernicus Query - Web Application

Interactive web interface for querying Copernicus Data Space products. Built with Streamlit - no command-line needed!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## 🌟 Features

- 🔍 **Visual Product Search** - Point-and-click interface
- 🗺️ **Spatial Filtering** - Preset locations or custom bounding box
- 📅 **Temporal Range** - Easy date selection
- 🎯 **Tile Support** - MGRS tile filtering for Sentinel-2
- 📥 **Download Formats** - Get `/eodata/` paths or detailed lists
- 🛰️ **Multi-Mission** - Sentinel-1, 2, and 3 support

## 🚀 Live Demo

[**Launch the App**](https://eopf-copernicus-query.streamlit.app) _(Will be available after deployment)_

## 📸 Preview

The app provides an intuitive interface with three main tabs:
- **Query Tab**: Configure and execute your product search
- **Results Tab**: View and download product lists
- **API Info Tab**: Documentation and usage guide

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **API**: Copernicus Data Space OData API
- **Deployment**: Streamlit Community Cloud (free)

## 🏃 Quick Start

### Run Locally

```bash
# Clone the repository
git clone https://github.com/Yuvraj198920/eopf-copernicus-query.git
cd eopf-copernicus-query

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run copernicus_query_app.py
```

The app will open in your browser at `http://localhost:8501`

### Using Docker

```bash
# Build the image
docker build -t eopf-copernicus-query .

# Run the container
docker run -p 8501:8501 eopf-copernicus-query
```

## 📖 How to Use

1. **Select Product Type**
   - Choose from Sentinel-2 L2A, Sentinel-3 OLCI, Sentinel-3 SLSTR, or Sentinel-1 GRD

2. **Configure Spatial Extent**
   - Use preset locations (e.g., Bolzano/South Tyrol)
   - Or enter custom coordinates (West, South, East, North)

3. **Set Temporal Range**
   - Pick start and end dates

4. **Execute Query**
   - Click the "🚀 Execute Query" button
   - Wait for results (usually < 30 seconds)

5. **Download Results**
   - View products in table
   - Download `/eodata/` paths or detailed format

## 📦 Supported Products

| Product | Collection | Description |
|---------|-----------|-------------|
| **Sentinel-2 L2A** | SENTINEL-2 | MSI Level-2A Bottom of Atmosphere Reflectance |
| **Sentinel-3 OLCI L1 EFR** | SENTINEL-3 | OLCI Level-1 Full Resolution |
| **Sentinel-3 SLSTR L1 RBT** | SENTINEL-3 | SLSTR Level-1 Radiances and Brightness Temperatures |
| **Sentinel-1 GRD** | SENTINEL-1 | SAR Ground Range Detected |

## 📥 Output Formats

### Format 1: /eodata/ Paths Only

Simple list, one path per line:
```text
/eodata/Sentinel-2/MSI/L2A_N0500/2017/09/01/S2A_MSIL2A_20170901T101021_N0500_R022_T32TPS_20230929T175520.SAFE
/eodata/Sentinel-2/MSI/L2A_N0500/2017/09/04/S2A_MSIL2A_20170904T102021_N0500_R065_T32TPS_20230930T014048.SAFE
```

### Format 2: Detailed Information

Includes metadata:
```text
1. S2A_MSIL2A_20170901T101021_N0500_R022_T32TPS_20230929T175520.SAFE
   Date: 2017-09-01 10:10:21
   Size: 850.01 MB
   Path: /eodata/Sentinel-2/MSI/L2A_N0500/2017/09/01/...
```

## 🌐 Deploy Your Own

### Streamlit Community Cloud (Free)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click "New app"
4. Select your forked repo
5. Set main file: `copernicus_query_app.py`
6. Click "Deploy"

### Other Platforms

- **Hugging Face Spaces**: Deploy as Streamlit Space
- **Railway**: Use included Dockerfile
- **Render**: Deploy with Docker or Python runtime

## 🔧 Configuration

The app uses `.streamlit/config.toml` for configuration:

```toml
[general]
email = ""

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

## 📚 API Documentation

This app uses the [Copernicus Data Space OData API](https://documentation.dataspace.copernicus.eu/APIs/OData.html):

- **Endpoint**: `https://catalogue.dataspace.copernicus.eu/odata/v1/Products`
- **Authentication**: Not required (public API)
- **Rate Limits**: None specified

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/Yuvraj198920/eopf-copernicus-query.git
cd eopf-copernicus-query

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run copernicus_query_app.py
```

## 📝 License

MIT License - see LICENSE file for details.

This project is part of the [EOPF Sample Notebooks](https://github.com/EOPF-Sample-Service/eopf-sample-notebooks) initiative.

## 🙏 Acknowledgments

- **Copernicus Data Space** for providing free access to Sentinel data
- **Streamlit** for the amazing web framework
- **EOPF Team** for supporting this project

## 📧 Contact

- **GitHub**: [@Yuvraj198920](https://github.com/Yuvraj198920)
- **Repository**: [eopf-copernicus-query](https://github.com/Yuvraj198920/eopf-copernicus-query)

## 🔗 Related Projects

- [EOPF Sample Notebooks](https://github.com/EOPF-Sample-Service/eopf-sample-notebooks)
- [Copernicus Data Space Documentation](https://documentation.dataspace.copernicus.eu/)

## ⭐ Star This Project

If you find this project useful, please consider giving it a star! ⭐

---

Made with ❤️ for the Earth Observation community