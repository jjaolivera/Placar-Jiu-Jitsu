from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from ui.tela_inicial import TelaInicial

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acesso Restrito - Sistema de Placar")
        self.setGeometry(600, 300, 350, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Digite a senha para acessar o sistema:")
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Entrar")
        self.login_btn.clicked.connect(self.check_password)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def check_password(self):
        if self.password_input.text() == "admin1310":
            self.close()
            self.open_main_app()
        else:
            QMessageBox.warning(self, "Erro", "Senha incorreta!")

    def open_main_app(self):
        self.main = TelaInicial()
        self.main.show()