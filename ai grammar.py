import sys
import json
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QComboBox, 
                             QLabel, QMessageBox, QFrame, QScrollArea, QGroupBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434"

# --- Stylesheets (Dark & Light) ---
DARK_THEME = """
QMainWindow { background-color: #1e1e1e; color: #ffffff; }
QWidget { background-color: #1e1e1e; color: #ffffff; }
QTextEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #444; padding: 10px; border-radius: 5px; }
QComboBox { background-color: #2d2d2d; color: #ffffff; border: 1px solid #444; padding: 5px; border-radius: 5px; }
QComboBox::drop-down { border: none; }
QPushButton { background-color: #007acc; color: white; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }
QPushButton:hover { background-color: #005f9e; }
QPushButton:disabled { background-color: #555; color: #888; }
QPushButton#CopyBtn { background-color: #2d2d2d; border: 1px solid #444; font-weight: normal; }
QPushButton#CopyBtn:hover { background-color: #3d3d3d; }
QLabel { color: #aaaaaa; font-size: 14px; }
QLabel#TitleLabel { color: #ffffff; font-size: 16px; font-weight: bold; }
QFrame { border: 1px solid #444; border-radius: 5px; }
QGroupBox { border: 1px solid #444; border-radius: 5px; margin-top: 10px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QScrollArea { border: none; background-color: transparent; }
"""

LIGHT_THEME = """
QMainWindow { background-color: #f0f0f0; color: #000000; }
QWidget { background-color: #f0f0f0; color: #000000; }
QTextEdit { background-color: #ffffff; color: #000000; border: 1px solid #ccc; padding: 10px; border-radius: 5px; }
QComboBox { background-color: #ffffff; color: #000000; border: 1px solid #ccc; padding: 5px; border-radius: 5px; }
QComboBox::drop-down { border: none; }
QPushButton { background-color: #007acc; color: white; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }
QPushButton:hover { background-color: #005f9e; }
QPushButton:disabled { background-color: #ccc; color: #666; }
QPushButton#CopyBtn { background-color: #ffffff; border: 1px solid #ccc; font-weight: normal; }
QPushButton#CopyBtn:hover { background-color: #e0e0e0; }
QLabel { color: #555555; font-size: 14px; }
QLabel#TitleLabel { color: #000000; font-size: 16px; font-weight: bold; }
QFrame { border: 1px solid #ccc; border-radius: 5px; }
QGroupBox { border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QScrollArea { border: none; background-color: transparent; }
"""

# --- Worker Thread for Ollama API ---
class OllamaWorker(QThread):
    finished = pyqtSignal(dict)  # Returns dict with 3 outputs
    error = pyqtSignal(str)
    models_loaded = pyqtSignal(list)

    def __init__(self, action, model_name=None, text=None):
        super().__init__()
        self.action = action
        self.model_name = model_name
        self.text = text

    def run(self):
        try:
            if self.action == 'list_models':
                response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = [m['name'] for m in data.get('models', [])]
                    self.models_loaded.emit(models)
                else:
                    self.error.emit("Failed to connect to Ollama. Is it running?")
            
            elif self.action == 'generate_all':
                # Three different prompts for three different outputs
                prompts = {
                    'grammar': f"Correct ONLY the grammar, spelling, and punctuation of the following text. Do not change the meaning or style. Output ONLY the corrected text:\n\n{self.text}",
                    'enhanced': f"Improve the following text by enhancing clarity, flow, and vocabulary while maintaining the original meaning. Make it sound more professional and polished. Output ONLY the improved text:\n\n{self.text}",
                    'alternative': f"Rewrite the following text in a completely different way while keeping the same core meaning. Provide an alternative phrasing. Output ONLY the rewritten text:\n\n{self.text}"
                }
                
                results = {}
                
                for key, prompt in prompts.items():
                    try:
                        payload = {
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.5 if key == 'alternative' else 0.3
                            }
                        }
                        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
                        if response.status_code == 200:
                            data = response.json()
                            results[key] = data.get('response', '').strip()
                        else:
                            results[key] = f"Error: {response.status_code}"
                    except Exception as e:
                        results[key] = f"Failed: {str(e)}"
                
                self.finished.emit(results)
                    
        except requests.exceptions.ConnectionError:
            self.error.emit("Cannot connect to Ollama. Ensure 'ollama serve' is running.")
        except Exception as e:
            self.error.emit(str(e))

# --- Output Panel Widget ---
class OutputPanel(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("TitleLabel")
        self.layout.addWidget(self.title_label)
        
        # Output Text
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Waiting for output...")
        self.output_text.setMinimumHeight(100)
        self.layout.addWidget(self.output_text)
        
        # Copy Button
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setObjectName("CopyBtn")
        self.copy_btn.setFixedWidth(80)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.layout.addWidget(self.copy_btn)
    
    def set_text(self, text):
        self.output_text.setText(text)
    
    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())

# --- Main Application Window ---
class GrammarFixerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.init_ui()
        self.load_models()

    def init_ui(self):
        self.setWindowTitle("Ollama Grammar Fixer - 3 Output Variations")
        self.setGeometry(100, 100, 900, 800)
        self.setStyleSheet(DARK_THEME)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Header / Controls ---
        header_layout = QHBoxLayout()
        
        self.model_label = QLabel("Select Model:")
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        
        self.refresh_btn = QPushButton("🔄 Refresh Models")
        self.refresh_btn.setFixedWidth(140)
        self.refresh_btn.clicked.connect(self.load_models)

        self.theme_btn = QPushButton("🎨 Toggle Theme")
        self.theme_btn.setFixedWidth(140)
        self.theme_btn.clicked.connect(self.toggle_theme)

        header_layout.addWidget(self.model_label)
        header_layout.addWidget(self.model_combo)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        header_layout.addWidget(self.theme_btn)

        # --- Input Area ---
        input_group = QGroupBox("📝 Input Text")
        input_layout = QVBoxLayout(input_group)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Type or paste your text here...")
        self.input_text.setMinimumHeight(120)
        input_layout.addWidget(self.input_text)
        
        # --- Action Button ---
        self.fix_btn = QPushButton("✨ Generate All 3 Versions")
        self.fix_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.fix_btn.setMinimumHeight(40)
        self.fix_btn.clicked.connect(self.start_fixing)
        input_layout.addWidget(self.fix_btn)

        # --- Output Area (3 Panels) ---
        output_group = QGroupBox("📤 Output Variations")
        output_layout = QVBoxLayout(output_group)
        
        # Scroll area for outputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_contents = QWidget()
        scroll_layout = QVBoxLayout(scroll_contents)
        scroll_layout.setSpacing(15)
        
        # Three output panels
        self.grammar_panel = OutputPanel("1️⃣ Grammar Fix (Corrections Only)")
        self.enhanced_panel = OutputPanel("2️⃣ Enhanced Version (Improved Flow & Vocabulary)")
        self.alternative_panel = OutputPanel("3️⃣ Alternative Version (Different Phrasing)")
        
        scroll_layout.addWidget(self.grammar_panel)
        scroll_layout.addWidget(self.enhanced_panel)
        scroll_layout.addWidget(self.alternative_panel)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_contents)
        output_layout.addWidget(scroll)

        # --- Status Bar ---
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")

        # Assemble Layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(input_group)
        main_layout.addWidget(output_group)
        main_layout.addWidget(self.status_label)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)

    def load_models(self):
        self.status_label.setText("Scanning for models...")
        self.model_combo.clear()
        self.worker = OllamaWorker('list_models')
        self.worker.models_loaded.connect(self.on_models_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_models_loaded(self, models):
        self.model_combo.addItems(models)
        if models:
            self.status_label.setText(f"Found {len(models)} models.")
        else:
            self.status_label.setText("No models found. Pull one via CLI (e.g., ollama pull llama3).")

    def start_fixing(self):
        model = self.model_combo.currentText()
        text = self.input_text.toPlainText().strip()

        if not model:
            self.on_error("No model selected.")
            return
        if not text:
            self.on_error("Input text is empty.")
            return

        self.status_label.setText("Generating 3 variations...")
        self.fix_btn.setEnabled(False)
        
        # Clear all outputs
        self.grammar_panel.set_text("")
        self.enhanced_panel.set_text("")
        self.alternative_panel.set_text("")

        self.worker = OllamaWorker('generate_all', model_name=model, text=text)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_generation_finished(self, results):
        self.grammar_panel.set_text(results.get('grammar', 'No output'))
        self.enhanced_panel.set_text(results.get('enhanced', 'No output'))
        self.alternative_panel.set_text(results.get('alternative', 'No output'))
        self.status_label.setText("Done - All 3 versions generated.")
        self.fix_btn.setEnabled(True)

    def on_error(self, message):
        self.status_label.setText("Error.")
        self.fix_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrammarFixerApp()
    window.show()
    sys.exit(app.exec_())