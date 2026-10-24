# Green Building Analyzer: AI-Powered Green Building and Material Footprint Analysis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23604851.svg)](https://doi.org/10.5281/zenodo.23604851)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-red.svg)](https://streamlit.io/)

Green Building Analyzer is a Python-based web application designed to help users explore the environmental impacts of building materials and compare material-selection scenarios. It combines material-footprint calculations, comparative analysis, and AI-assisted recommendations in an interactive interface.

The project is intended as a software tool for sustainable construction exploration, educational use, and further research and development.

**Live application:** [Open Green Building Analyzer](https://green-building-analyzer-xbwtufdrcywjjthgika3iw.streamlit.app/)

**Source code:** [GitHub Repository](https://github.com/rajuakhand/green-building-analyzer)

**Software DOI:** [10.5281/zenodo.23604851](https://doi.org/10.5281/zenodo.23604851)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Testing](#testing)
- [Methodology and Interpretation](#methodology-and-interpretation)
- [Limitations](#limitations)
- [Citation](#citation)
- [AI-Assisted Development](#ai-assisted-development)
- [License](#license)
- [Author](#author)

## Overview

Building materials can contribute significantly to the environmental impacts associated with construction. Comparing materials and alternative design scenarios can help users investigate potential opportunities to reduce embodied carbon.

Green Building Analyzer provides an interactive environment for exploring material-related footprint estimates and reviewing sustainability recommendations. The application is built with Python and Streamlit, with data processing and visualization features intended to support analysis.

## Features

- **Material footprint analysis:** Explore estimated environmental impacts associated with supported building materials, such as concrete, steel, glass, and wood, where available in the application.
- **AI-assisted recommendations:** Generate sustainability suggestions using the Google Gemini API when configured.
- **Comparative analysis:** Compare supported materials or building scenarios using the application's available analysis features.
- **Interactive dashboard:** Explore inputs and results through a Streamlit web interface.
- **Data export:** Export supported analysis results in formats provided by the application, including CSV and PDF.
- **Testing:** Run the project's automated tests to check supported software functionality.
- **Open-source availability:** Review, use, and modify the code under the terms of the MIT License.

Feature availability may depend on the current application version and configuration.

## Technology Stack

- **Python:** Core application logic
- **Streamlit:** Interactive web interface
- **Pandas:** Data processing and tabular analysis
- **Plotly:** Interactive data visualization, where used
- **Google Gemini API:** AI-assisted sustainability recommendations
- **Pytest:** Automated testing, where configured in the project

## Getting Started

### Prerequisites

- Python 3.9 or a compatible version supported by the project's dependencies
- Git
- An internet connection to clone the repository and install dependencies
- A Google Gemini API key if you want to use the AI recommendation features

### 1. Clone the repository

```bash
git clone https://github.com/rajuakhand/green-building-analyzer.git
cd green-building-analyzer
```

### 2. Create a virtual environment

**macOS or Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to use the application.

If a command or dependency differs in the current repository, follow the project's actual configuration files.

## Configuration

Some features may require API credentials.

If you use Google Gemini-powered recommendations:

1. Obtain an API key through the official Google AI developer platform.
2. Configure the key using the application's supported secrets or environment-variable mechanism.
3. Keep API credentials private.
4. Never commit API keys, passwords, or other secrets to GitHub.

Refer to the current source code and deployment configuration for the exact variable name or secrets format required by the application.

## Testing

Run the project's automated tests from the repository root:

```bash
python -m pytest -q
```

A passing test suite indicates that the tested behaviors passed under the test environment. It does not, by itself, establish the scientific accuracy of all carbon-footprint estimates or validate every possible input.

For reproducible evaluation, document the Python version, dependency versions, test results, and any additional checks performed.

## Methodology and Interpretation

Material-footprint estimates generally depend on the quantity of each material and the emission factor selected for that material.

A commonly used calculation structure is:

**Estimated material emissions = Material quantity × Applicable emission factor**

The units must be compatible. For example, a material quantity expressed in kilograms should be paired with an emission factor expressed per kilogram.

The reliability of an estimate depends on factors such as:

- The source and geographic applicability of emission factors
- Material type, grade, and production process
- The system boundary used, such as cradle-to-gate or another life-cycle boundary
- Transportation, construction, maintenance, and end-of-life stages, if included
- The units, assumptions, and data quality of the input values

The formula above describes a general calculation principle; it should not be interpreted as a complete description of every calculation implemented in this software. Consult the source code and data files to determine the application's actual methodology and assumptions.

## Limitations

- Results depend on the input values, emission factors, assumptions, and calculation methods used by the application.
- Estimates should not be interpreted as independently verified life-cycle assessments unless the underlying data and methodology have been validated for that purpose.
- AI-generated recommendations may be incomplete or inaccurate and should be reviewed before practical use.
- Results may not represent all stages of a building's life cycle.
- The software is intended to support analysis and exploration; it does not replace professional engineering advice, verified environmental product declarations, or a formal life-cycle assessment.

## Citation

If you use this software in academic work, please cite the corresponding archived software release. Verify that the DOI resolves to the correct record and that the author, release version, and publication date match the archived metadata.

### BibTeX

```bibtex
@software{Akhand_Green_Building_Analyzer,
  author    = {Akhand, Abdul Gaffar Raju},
  title     = {{Green Building Analyzer: AI-Powered Green Building and Material Footprint Analysis}},
  publisher = {Zenodo},
  year      = {2026},
  version   = {v1.0.0},
  doi       = {10.5281/zenodo.23604851},
  url       = {https://doi.org/10.5281/zenodo.23604851}
}
```

Check the Zenodo record before using this citation. In particular, ensure that the title and version match the deposited release.

## AI-Assisted Development

The author independently developed this project and used AI-assisted tools to support debugging and error identification. The author is responsible for reviewing the implementation, checking outputs, and approving the final software.

AI assistance does not replace the need to verify calculations, document sources, test the application, and report limitations. Any future academic manuscript based on this software will follow the AI-use and authorship requirements of its intended publication venue.

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for the applicable terms.

## Author

**Abdul Gaffar Raju Akhand**

- GitHub: [rajuakhand](https://github.com/rajuakhand)
- Project repository: [green-building-analyzer](https://github.com/rajuakhand/green-building-analyzer)
- Live application: [Green Building Analyzer](https://green-building-analyzer-xbwtufdrcywjjthgika3iw.streamlit.app/)

## Acknowledgements

The author acknowledges the guidance received from a teacher during project development and the use of AI-assisted tools for debugging support.

---

*This README describes the project's intended functionality. Claims about scientific validation, quantitative accuracy, and performance should be supported by documented methods and reproducible evaluation results.*
   ```bash
   git clone [https://github.com/rajuakhand/green-building-analyzer.git](https://github.com/rajuakhand/green-building-analyzer.git)
   cd green-building-analyzer
