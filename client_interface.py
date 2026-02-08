import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QTimer
from main import main


class Worker(QThread):
    finished = pyqtSignal(str)

    def run(self):
        pdf_path = main()
        self.finished.emit(pdf_path)


class PDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relatório de Ações de Rating")
        self.setGeometry(100, 100, 1000, 700)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        self.btn_generate = QPushButton("Gerar PDF")
        self.btn_generate.clicked.connect(self.generate_pdf)
        self.layout.addWidget(self.btn_generate, 0)

        self.label_status = QLabel("Pronto para gerar relatório.")
        self.layout.addWidget(self.label_status, 0)

        self.pdf_view = QWebEngineView()
        self.pdf_view.settings().setAttribute(
            QWebEngineSettings.PluginsEnabled, True
        )
        self.layout.addWidget(self.pdf_view, 1)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: Segoe UI, Arial;
                font-size: 14px;
            }

            QPushButton {
                background-color: #E57200;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #ff8c1a;
            }

            QPushButton:pressed {
                background-color: #cc6400;
            }

            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }

            QLabel {
                background-color: #1e1e1e;
                padding: 6px;
                border-radius: 6px;
                color: #cccccc;
            }

            QWebEngineView {
                border-radius: 10px;
                background-color: white;
                border: 1px solid #333333;
            }
        """)

    def generate_pdf(self):
        self.label_status.setText("Gerando PDF, aguarde...")
        self.btn_generate.setEnabled(False)

        self.worker = Worker()
        self.worker.finished.connect(self.show_pdf)
        self.worker.start()

    def show_pdf(self, pdf_path):
        self.btn_generate.setEnabled(True)

        abs_path = os.path.abspath(pdf_path)

        if not os.path.exists(abs_path):
            self.label_status.setText("Erro: PDF não encontrado.")
            return

        self.label_status.setText(f"PDF gerado: {abs_path}")

        url = QUrl.fromLocalFile(abs_path)
        self.pdf_view.setUrl(url)

        QTimer.singleShot(800, self.pdf_view.reload)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFApp()
    window.show()
    sys.exit(app.exec_())
