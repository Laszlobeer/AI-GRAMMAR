# 🦙 Ollama Grammar Fixer

A lightweight desktop application built with **PyQt5** that leverages your local **Ollama** instance to correct, enhance, and rewrite text. This tool runs entirely offline (depending on your model) and provides three distinct variations of your input text simultaneously.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Latest-orange.svg)

## ✨ Features

- **🔄 3-in-1 Output Generation**:
  1.  **Grammar Fix**: Corrects spelling, punctuation, and grammar without changing style.
  2.  **Enhanced Version**: Improves clarity, flow, and vocabulary for a professional tone.
  3.  **Alternative Version**: Rewrites the text with completely different phrasing while keeping the core meaning.
- **🌙 Dark & Light Themes**: Toggle between interfaces to suit your environment.
- **🤖 Local LLM Support**: Works with any model loaded in your local Ollama instance (e.g., Llama 3, Mistral, Gemma).
- **📋 One-Click Copy**: Easily copy any of the generated results to your clipboard.
- **🔌 Automatic Model Detection**: Scans your local Ollama instance for available models.

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

1.  **Python 3.7 or higher**
2.  **Ollama**: Installed and running locally.
    - Download from [ollama.com](https://ollama.com)
    - Ensure the server is running (`ollama serve`).
    - Pull at least one model (e.g., `ollama pull llama3`).
3.  **Python Dependencies**:
    ```bash
    pip install PyQt5 requests
    ```

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/laszlobeer/ollama-grammar-fixer.git](https://github.com/Laszlobeer/AI-GRAMMAR.git)
    cd ollama-grammar-fixer
    ```

2.  **Verify Ollama is running**:
    Open a terminal and check if Ollama is active:
    ```bash
    ollama list
    ```

3.  **Run the Application**:
    ```bash
    python "ai grammar.py"
    ```

## 📖 Usage

1.  **Launch the App**: Start the script using the command above.
2.  **Select Model**: Use the dropdown menu at the top to choose an installed Ollama model. Click **🔄 Refresh Models** if your list is empty.
3.  **Input Text**: Type or paste the text you want to process in the **Input Text** area.
4.  **Generate**: Click the **✨ Generate All 3 Versions** button.
5.  **Review Outputs**:
    - View the corrections, enhancements, and alternatives in the respective panels below.
    - Click **📋 Copy** on any panel to copy the text to your clipboard.
6.  **Toggle Theme**: Click **🎨 Toggle Theme** to switch between Dark and Light modes.

## ⚙️ Configuration

You can modify the API endpoint if your Ollama instance is running on a non-default port or host.

Open `ai grammar.py` and edit the following line near the top:

```python
OLLAMA_URL = "http://localhost:11434"
```


---

**Made with ❤️ and 🦙**
