import sys
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QLineEdit
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap


# ================== TELÃO (EXIBIÇÃO) ==================
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

        # ===== TOPO: LOGO + CRONÔMETRO =====
        top_layout = QHBoxLayout()

        # Logo no canto superior esquerdo
        self.logo_label = QLabel()
        pixmap = QPixmap("logo.png") # Coloque o caminho da sua imagem aqui
        if not pixmap.isNull():
            pixmap = pixmap.scaledToHeight(120, Qt.SmoothTransformation)# type: ignore
            self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # type: ignore
        top_layout.addWidget(self.logo_label, alignment=Qt.AlignLeft)# type: ignore

        # Cronômetro
        self.timer_label = QLabel(tempo_texto)
        self.timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.timer_label.setStyleSheet(
            "font-size:150px; font-weight:900; color:white;"
        )
        self.timer_label.setFixedHeight(140)
        top_layout.addWidget(self.timer_label, stretch=1)

        top_layout.addStretch()
        main.addLayout(top_layout)

        # ===== PLACAR DOS ATLETAS =====
        board = QHBoxLayout()
        main.addLayout(board)

        board.addWidget(self._build_side("A", atleta1, "white"))
        board.addWidget(self._build_side("B", atleta2, "#199649"))

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
        lbl_points.setStyleSheet("font-size:250px; font-weight:900; color:black;")
        layout.addWidget(lbl_points)

        # Linha com Vantagem (azul) e Punição (vermelho) lado a lado
        bottom = QHBoxLayout()

        vant = QFrame()
        vant.setStyleSheet("background:#0181ba; border:none;")
        vant_layout = QVBoxLayout(vant)
        lbl_v = QLabel("0")
        lbl_v.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_v.setStyleSheet("font-size:80px; font-weight:900; color:black;")
        vant_layout.addWidget(lbl_v)
        bottom.addWidget(vant)

        pen = QFrame()
        pen.setStyleSheet("background:red; border:none;")
        pen_layout = QVBoxLayout(pen)
        lbl_p = QLabel("0")
        lbl_p.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_p.setStyleSheet("font-size:80px; font-weight:900; color:black;")
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


# ================== CONTROLE ==================
class PlacarControle(QWidget):
    """Tela de controle do placar"""
    def __init__(self, exibicao: PlacarExibicao, tempo_inicial, nomeA, nomeB):
        super().__init__()
        self.exibicao = exibicao
        self.setWindowTitle("Placar - Controle")
        self.setGeometry(50, 50, 1100, 650)
        self.setStyleSheet("background-color: #222; color: white;")

        self.nomeA = nomeA
        self.nomeB = nomeB

        # Estado
        self.state = {
            'A': {'points': 0, 'advantages': 0, 'penalties': 0},
            'B': {'points': 0, 'advantages': 0, 'penalties': 0}
        }

        # Timer
        self.initial_secs = tempo_inicial
        self.remaining = self.initial_secs
        self.running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        # Layout principal
        main = QVBoxLayout(self)

        # Cronômetro
        self.timer_label = QLabel(self._fmt(self.remaining))
        self.timer_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.timer_label.setStyleSheet(
            "font-size:50px; font-weight:900; color:#0f0; background:#000;"
        )
        self.timer_label.setFixedHeight(80)
        main.addWidget(self.timer_label)

        # (Opcional) alterar tempo durante o evento
        time_setter = QHBoxLayout()
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Tempo (min)")
        self.time_input.setFixedWidth(110)
        btn_set_time = QPushButton("Definir Tempo")
        btn_set_time.clicked.connect(self.set_time)
        time_setter.addWidget(self.time_input)
        time_setter.addWidget(btn_set_time)
        main.addLayout(time_setter)

        # Área dos atletas
        board = QHBoxLayout()
        board.addWidget(self._build_side("A", self.nomeA))
        board.addWidget(self._build_side("B", self.nomeB))
        main.addLayout(board)

        # Controles do cronômetro
        timer_controls = QHBoxLayout()
        for text, func in [
            ("▶ Iniciar", self.start),
            ("⏸ Pausar", self.pause),
            ("⏹ Resetar", self.reset),
            ("🔄 Resetar Tudo", self.reset_all),  # Novo botão
            ("⛶ Tela Cheia", self.exibicao.toggle_fullscreen)
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet("font-size:20px; padding:10px;")
            btn.clicked.connect(func)
            timer_controls.addWidget(btn)
        main.addLayout(timer_controls)

        self.update_exibicao()

    def _build_side(self, side, name):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Nome
        lbl_name = QLabel(name)
        lbl_name.setAlignment(Qt.AlignCenter)  # type: ignore
        lbl_name.setStyleSheet("font-size:24px; font-weight:700;")
        layout.addWidget(lbl_name)

        # Pontos atuais (mostra no controle)
        self.__dict__[f"lbl_{side}_points"] = QLabel("0")
        self.__dict__[f"lbl_{side}_points"].setAlignment(Qt.AlignCenter)  # type: ignore
        self.__dict__[f"lbl_{side}_points"].setStyleSheet("font-size:60px; font-weight:900;")
        layout.addWidget(self.__dict__[f"lbl_{side}_points"])

        # Cores diferentes para cada lado
        if side == "A":
            cor = "white"   # igual à exibição
        else:
            cor = "#199649"  # verde igual ao lado B da exibição

        self.__dict__[f"lbl_{side}_points"].setStyleSheet(
        f"font-size:60px; font-weight:900; color:{cor};"
    )
        layout.addWidget(self.__dict__[f"lbl_{side}_points"])

        # Botões pontuação (padrão IBJJF)
        pts = QHBoxLayout()
        for label, val in [("Queda/Rasp +2", 2), ("Passagem +3", 3), ("Montada/Costas +4", 4), ("-1 ponto", -1)]:
            b = QPushButton(label)
            b.clicked.connect(partial(self._change, side, "points", val))
            pts.addWidget(b)
        layout.addLayout(pts)

        # Vantagem e Punição (com botões + e -)
        adv_pen = QHBoxLayout()
        for metric, titulo in [("advantages", "Vantagem"), ("penalties", "Punição")]:
            sub = QVBoxLayout()
            lbl = QLabel(f"{titulo}: 0")
            self.__dict__[f"lbl_{side}_{metric}"] = lbl
            sub.addWidget(lbl)
            btns = QHBoxLayout()
            for t, v in [("+", 1), ("−", -1)]:
                b = QPushButton(f"{titulo} {t}")
                b.clicked.connect(partial(self._change, side, metric, v))
                btns.addWidget(b)
            sub.addLayout(btns)
            adv_pen.addLayout(sub)
        layout.addLayout(adv_pen)

        return frame

    # ===== Lógica =====
    def _change(self, side, metric, delta):
        new_val = max(0, self.state[side][metric] + delta)
        self.state[side][metric] = new_val
        self._update_labels()
        self.update_exibicao()

    def _update_labels(self):
        for side in ("A", "B"):
            self.__dict__[f"lbl_{side}_points"].setText(str(self.state[side]["points"]))
            self.__dict__[f"lbl_{side}_advantages"].setText(f"Vantagem: {self.state[side]['advantages']}")
            self.__dict__[f"lbl_{side}_penalties"].setText(f"Punição: {self.state[side]['penalties']}")

    def _fmt(self, s):
        m, sec = divmod(int(s), 60)
        return f"{m:02}:{sec:02}"

    def _tick(self):
        if self.running and self.remaining > 0:
            self.remaining -= 1
            self.timer_label.setText(self._fmt(self.remaining))
            self.update_exibicao()

    def start(self):
        if not self.running:
            self.running = True
            self.timer.start(1000)

    def pause(self):
        self.running = False
        self.timer.stop()

    def reset(self):
        self.pause()
        self.remaining = self.initial_secs
        self.timer_label.setText(self._fmt(self.remaining))
        self.update_exibicao()

    def reset_all(self):
        """Reseta tempo + placares"""
        self.pause()
        self.remaining = self.initial_secs
        for side in ("A", "B"):
            self.state[side] = {"points": 0, "advantages": 0, "penalties": 0}
        self._update_labels()
        self.update_exibicao()
        self.timer_label.setText(self._fmt(self.remaining))

    def set_time(self):
        try:
            minutes = int(self.time_input.text())
            self.initial_secs = minutes * 60
            self.reset_all()
        except ValueError:
            self.time_input.setText("Erro")

    def update_exibicao(self):
        self.exibicao.update_display(self.state, self._fmt(self.remaining))

    # ===== Atalhos de teclado =====
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:  # type: ignore
            self.pause() if self.running else self.start()
        elif key == Qt.Key_R:  # type: ignore
            self.reset()
        elif key == Qt.Key_T:  # type: ignore
            self.reset_all()
        elif key == Qt.Key_F:  # type: ignore
            self.exibicao.toggle_fullscreen()

        # Atleta A
        elif key == Qt.Key_1: self._change("A", "points", 2)  # type: ignore
        elif key == Qt.Key_2: self._change("A", "points", 3)  # type: ignore
        elif key == Qt.Key_3: self._change("A", "points", 4)  # type: ignore
        elif key == Qt.Key_4: self._change("A", "points", -1)  # type: ignore
        elif key == Qt.Key_Q: self._change("A", "advantages", 1)  # type: ignore
        elif key == Qt.Key_A: self._change("A", "advantages", -1)  # type: ignore
        elif key == Qt.Key_W: self._change("A", "penalties", 1)  # type: ignore
        elif key == Qt.Key_S: self._change("A", "penalties", -1)  # type: ignore

        # Atleta B
        elif key == Qt.Key_7: self._change("B", "points", 2)  # type: ignore
        elif key == Qt.Key_8: self._change("B", "points", 3)  # type: ignore
        elif key == Qt.Key_9: self._change("B", "points", 4)  # type: ignore
        elif key == Qt.Key_0: self._change("B", "points", -1)  # type: ignore
        elif key == Qt.Key_U: self._change("B", "advantages", 1)  # type: ignore
        elif key == Qt.Key_J: self._change("B", "advantages", -1)  # type: ignore
        elif key == Qt.Key_I: self._change("B", "penalties", 1)  # type: ignore
        elif key == Qt.Key_K: self._change("B", "penalties", -1)  # type: ignore


# ================== TELA INICIAL ==================
class TelaInicial(QWidget):
    """Tela inicial para configurar nomes e tempo"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração da Luta")
        self.setGeometry(300, 200, 420, 300)
        self.setStyleSheet("background:#333; color:white; font-size:18px;")

        layout = QVBoxLayout(self)

        # Nome Atleta 1
        self.atleta1_input = QLineEdit()
        self.atleta1_input.setPlaceholderText("Nome Atleta 1")
        layout.addWidget(self.atleta1_input)

        # Nome Atleta 2
        self.atleta2_input = QLineEdit()
        self.atleta2_input.setPlaceholderText("Nome Atleta 2")
        layout.addWidget(self.atleta2_input)

        # Tempo
        self.tempo_input = QLineEdit()
        self.tempo_input.setPlaceholderText("Tempo (min)")
        layout.addWidget(self.tempo_input)

        # Botão iniciar
        btn_start = QPushButton("Iniciar Luta")
        btn_start.clicked.connect(self.iniciar)
        layout.addWidget(btn_start)

    def iniciar(self):
        atleta1 = self.atleta1_input.text().strip() #or "Atleta 1"
        atleta2 = self.atleta2_input.text().strip() #or "Atleta 2"
        try:
            minutos = int(self.tempo_input.text())
        except:
            minutos = 5
        tempo_segundos = minutos * 60
        tempo_texto = f"{minutos:02}:00"

        # Criar telas
        exibicao = PlacarExibicao(atleta1, atleta2, tempo_texto)
        exibicao.show()
        controle = PlacarControle(exibicao, tempo_segundos, atleta1, atleta2)
        controle.show()

        self.close()


# ================== MAIN ==================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = TelaInicial()
    menu.show()
    sys.exit(app.exec_())
