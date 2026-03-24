import sys
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QShortcut, QSpinBox, QMessageBox,)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import QTimer, Qt

class PlacarExibicao(QWidget):
    """Tela do telão (exibição)"""
    def __init__(self, atleta1, atleta2, tempo_texto):
        super().__init__()
        self.setWindowTitle("Placar - Exibição")
        self.setStyleSheet("background-color: #111; color: black;")
        self.showMaximized()

        # Referências dos labels (cria ANTES de montar os lados)
        self.labels = {
            "A": {"points": None, "advantages": None, "penalties": None},
            "B": {"points": None, "advantages": None, "penalties": None}
        }

        # Layout principal
        main = QVBoxLayout(self)
        
        # Topo com logo à esquerda e cronômetro centralizado
        top_layout = QHBoxLayout()
        
        # Logo no canto esquerdo
        self.logo_label = QLabel()
        pixmap = QPixmap("assets/logo2.png")  # Coloque o caminho da sua imagem aqui
        if not pixmap.isNull():
            pixmap = pixmap.scaledToHeight(250, Qt.SmoothTransformation)  # type: ignore
            self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # type: ignore
        top_layout.addWidget(self.logo_label)
        
        # Cronômetro centralizado na tela
        self.timer_label = QLabel(tempo_texto)
        self.timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.timer_label.setStyleSheet(
            "font-size:250px; font-weight:900; color:white;"
        )
        self.timer_label.setFixedHeight(250)
        
        # Centralizar o cronômetro na tela inteira
        top_layout.addStretch(1)
        top_layout.addWidget(self.timer_label)
        top_layout.addStretch(1)
        
        # Espaço vazio à direita para balancear o logo (mesmo tamanho do logo)
        empty_label = QLabel()
        empty_label.setFixedSize(self.logo_label.sizeHint())
        top_layout.addWidget(empty_label)
        
        main.addLayout(top_layout)

        # ===== PLACAR DOS ATLETAS =====
        board = QHBoxLayout()
        
        # Placar do atleta A (esquerda)
        board.addWidget(self._build_side("A", atleta1, "white"))
        
        # Placar do atleta B (direita)
        board.addWidget(self._build_side("B", atleta2, "#199649"))
        
        main.addLayout(board)

        # Atalho F11 para o telão
        shortcut_fullscreen = QShortcut(QKeySequence("F11"), self)
        shortcut_fullscreen.activated.connect(self.toggle_fullscreen)

        # controla se está vermelho ou branco
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.blink_state = False  


    def _build_side(self, side, name, color):
        frame = QFrame()
        frame.setStyleSheet(f"background:{color};")
        layout = QVBoxLayout(frame)

        # Nome
        lbl_name = QLabel(name)
        lbl_name.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_name.setStyleSheet("font-size:36px; font-weight:700; color:black;")
        layout.addWidget(lbl_name)

        # Pontos principais
        lbl_points = QLabel("0")
        lbl_points.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_points.setStyleSheet("font-size:350px; font-weight:900; color:black;")
        layout.addWidget(lbl_points)

        # Linha com Vantagem (azul) e Punição (vermelho) lado a lado
        bottom = QHBoxLayout()

        vant = QFrame()
        vant.setStyleSheet("background:#0181ba; border:none;")
        vant_layout = QVBoxLayout(vant)
        lbl_v = QLabel("0")
        lbl_v.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_v.setStyleSheet("font-size:150px; font-weight:900; color:black;")
        vant_layout.addWidget(lbl_v)
        bottom.addWidget(vant)

        pen = QFrame()
        pen.setStyleSheet("background:red; border:none;")
        pen_layout = QVBoxLayout(pen)
        lbl_p = QLabel("0")
        lbl_p.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_p.setStyleSheet("font-size:150px; font-weight:900; color:black;")
        pen_layout.addWidget(lbl_p)
        bottom.addWidget(pen)

        layout.addLayout(bottom)

        # Guardar refs pelo lado
        self.labels[side]["points"] = lbl_points  # type: ignore
        self.labels[side]["advantages"] = lbl_v  # type: ignore
        self.labels[side]["penalties"] = lbl_p  # type: ignore

        return frame

    def update_display(self, state, timer_text):
        """Atualiza os valores no telão"""
        self.timer_label.setText(timer_text)
        for side in ("A", "B"):
            self.labels[side]["points"].setText(str(state[side]["points"]))  # type: ignore
            self.labels[side]["advantages"].setText(str(state[side]["advantages"]))  # type: ignore
            self.labels[side]["penalties"].setText(str(state[side]["penalties"]))  # type: ignore

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # Deixa o cronometro vermelho quando pausado 
    def set_timer_paused(self, paused: bool):
        """Quando pausado, cronômetro pisca em vermelho; senão, fica branco fixo"""
        if paused:
            self.blink_timer.start(500)  # alterna a cada 500ms
        else:
            self.blink_timer.stop()
            self.timer_label.setStyleSheet("font-size:250px; font-weight:900; color:white;")
            self.blink_state = False

    def _toggle_blink(self):
        """Alterna entre vermelho e branco"""
        if self.blink_state:
            self.timer_label.setStyleSheet("font-size:250px; font-weight:900; color:white;")
        else:
            self.timer_label.setStyleSheet("font-size:250px; font-weight:900; color:red;")
        self.blink_state = not self.blink_state
