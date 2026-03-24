from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton
from ui.exibicao import PlacarExibicao
from ui.controle import PlacarControle

class TelaInicial(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração da Luta")
        self.setGeometry(300, 200, 420, 300)

        layout = QVBoxLayout(self)

        self.atleta1_input = QLineEdit()
        self.atleta1_input.setPlaceholderText("Nome Atleta 1")
        layout.addWidget(self.atleta1_input)

        self.atleta2_input = QLineEdit()
        self.atleta2_input.setPlaceholderText("Nome Atleta 2")
        layout.addWidget(self.atleta2_input)

        self.tempo_input = QLineEdit()
        self.tempo_input.setPlaceholderText("Tempo (min)")
        layout.addWidget(self.tempo_input)

        btn_start = QPushButton("Iniciar Luta")
        btn_start.clicked.connect(self.iniciar)
        layout.addWidget(btn_start)

    def iniciar(self):
        atleta1 = self.atleta1_input.text().strip()
        atleta2 = self.atleta2_input.text().strip()
        minutos = int(self.tempo_input.text() or 5)

        tempo_segundos = minutos * 60
        tempo_texto = f"{minutos:02}:00"

        exibicao = PlacarExibicao(atleta1, atleta2, tempo_texto)
        exibicao.show()

        controle = PlacarControle(exibicao, tempo_segundos, atleta1, atleta2)
        controle.show()

        self.close()