import sys
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QShortcut, QSpinBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import QTimer, Qt

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
        
        # Topo com logo à esquerda e cronômetro centralizado
        top_layout = QHBoxLayout()
        
        # Logo no canto esquerdo
        self.logo_label = QLabel()
        pixmap = QPixmap("logo.png")  # Coloque o caminho da sua imagem aqui
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
            "font-size:150px; font-weight:900; color:white; background:#000;"
        )
        self.timer_label.setFixedHeight(150)
        main.addWidget(self.timer_label)

        # (Opcional) alterar tempo durante o evento
        time_setter = QHBoxLayout()

        # Campo para minutos
        self.minutes_input = QSpinBox()  # type: ignore
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setSuffix(" min")
        self.minutes_input.setFixedWidth(150)
        self.minutes_input.setMinimumHeight(50)
        self.minutes_input.setStyleSheet("font-size:30px; padding:10px;")

        # Campo para segundos
        self.seconds_input = QSpinBox()  # type: ignore
        self.seconds_input.setRange(0, 59)
        self.seconds_input.setSuffix(" s")
        self.seconds_input.setFixedWidth(150)
        self.minutes_input.setMinimumHeight(50)
        self.seconds_input.setStyleSheet("font-size:30px; padding:10px;")

        # Botão para definir
        btn_set_time = QPushButton("Definir Tempo")
        btn_set_time.clicked.connect(self.set_time)
        #btn_set_time.setFixedSize(1000, 60)  # largura x altura
        btn_set_time.clicked.connect(self.set_time)
        btn_set_time.setStyleSheet("font-size:30px; padding:10px;")

        # Adiciona ao layout
        time_setter.addWidget(self.minutes_input)
        time_setter.addWidget(self.seconds_input)
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
            ("▶ Iniciar (I)", self.start),
            ("⏸ Pausar (P)", self.pause),
            ("⏹ Reset. Tempo (T)", self.reset),
            ("🔄 Resetar Tudo (R)", self.reset_all),  # Novo botão
            ("⛶ Tela Cheia (F11)", self.exibicao.toggle_fullscreen)
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet("font-size:25px; padding:10px;")
            btn.clicked.connect(func)
            timer_controls.addWidget(btn)
        main.addLayout(timer_controls)

        self.update_exibicao()

        # Atalho para fullscreen da tela de controle (F10)
        shortcut_fullscreen = QShortcut(QKeySequence("F10"), self)
        shortcut_fullscreen.activated.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
        """Alterna entre fullscreen e modo janela na tela de controle"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

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
        self.__dict__[f"lbl_{side}_points"].setStyleSheet("font-size:250px; font-weight:900;")
        layout.addWidget(self.__dict__[f"lbl_{side}_points"])

        # Cores diferentes para cada lado
        if side == "A":
            cor = "white"   # igual à exibição
        else:
            cor = "#199649"  # verde igual ao lado B da exibição

        self.__dict__[f"lbl_{side}_points"].setStyleSheet(
            f"font-size:250px; font-weight:900; color:{cor};"
        )
        layout.addWidget(self.__dict__[f"lbl_{side}_points"])

        # Botões pontuação (padrão IBJJF)
        pts = QHBoxLayout()

        cores = {
            "+2": "white",
            "+3": "white",
            "+4": "white",
            "-1": "red"
        }

        for label, val in [("+2", 2), ("+3", 3), ("+4", 4), ("-1", -1)]:
            b = QPushButton(label)
            cor = cores[label]
            b.setStyleSheet(f"font-size:45px; font-weight:900; color:{cor}; min-width:100px; min-height:60px;")
            b.clicked.connect(partial(self._change, side, "points", val))
            pts.addWidget(b)

        layout.addLayout(pts)

        # Vantagem e Punição (com botões + e -)
        adv_pen = QHBoxLayout()
        cores_metricas = {
            "V +": "#1591EA",
            "V −": "red",
            "P +": "#1591EA",
            "P −": "red"
        }

        for metric, titulo in [("advantages", "V"), ("penalties", "P")]:
            sub = QVBoxLayout()
            lbl = QLabel(f"{titulo}: 0")
            lbl.setAlignment(Qt.AlignCenter)  # type: ignore
            lbl.setStyleSheet(
                "font-size:40px; font-weight:700; color:white; padding:5px; border-radius:10px;"
            )
            self.__dict__[f"lbl_{side}_{metric}"] = lbl
            sub.addWidget(lbl)

            btns = QHBoxLayout()
            for t, v in [("+", 1), ("−", -1)]:
                text = f"{titulo} {t}"
                b = QPushButton(text)

                # Aplica a cor de acordo com o dicionário
                cor = cores_metricas[text]
                b.setStyleSheet(
                    f"font-size:24px; font-weight:700; color:{cor}; "
                    "min-width:110px; min-height:50px;"
                )

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
            self.__dict__[f"lbl_{side}_advantages"].setText(f"V: {self.state[side]['advantages']}")
            self.__dict__[f"lbl_{side}_penalties"].setText(f"P: {self.state[side]['penalties']}")

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
            # volta a cor para branco quando iniciar
            self.timer_label.setStyleSheet("font-size:150px; font-weight:900; color:white; background:#000;")
            self.exibicao.set_timer_paused(False)  # <<< volta ao branco no telão

    def pause(self):
        self.running = False
        self.timer.stop()
        self.timer_label.setStyleSheet(
            "font-size:150px; font-weight:900; color:red; background:#000;"
        )
        self.exibicao.set_timer_paused(True)  # ativa piscar no telão

    def reset(self):
        self.pause()
        self.remaining = self.initial_secs
        self.timer_label.setText(self._fmt(self.remaining))
        self.update_exibicao()

    def reset_all(self):
        self.pause()
        self.remaining = self.initial_secs
        for side in ("A", "B"):
            self.state[side] = {"points": 0, "advantages": 0, "penalties": 0}
        self._update_labels()
        self.update_exibicao()
        self.timer_label.setText(self._fmt(self.remaining))

        # volta cor normal no controle
        self.timer_label.setStyleSheet(
            "font-size:150px; font-weight:900; color:white; background:#000;"
        )

        # desliga piscar no telão
        self.exibicao.set_timer_paused(False)

        # Voltar a cor do cronômetro no controle
        self.timer_label.setStyleSheet(
            "font-size:150px; font-weight:900; color:white; background:#000;"
        )

        # Voltar a cor do cronômetro no telão
        try:
            self.exibicao.set_timer_paused(False)
        except Exception:
            pass

    def set_time(self):
        minutes = self.minutes_input.value()
        seconds = self.seconds_input.value()
        self.initial_secs = minutes * 60 + seconds
        self.remaining = self.initial_secs
        # Atualiza o label do timer para refletir o novo tempo
        self.update_timer_display()
        self.update_exibicao()

    def update_timer_display(self):
        """Atualiza o label do cronômetro na tela de controle"""
        self.timer_label.setText(self._fmt(self.remaining))

    def update_exibicao(self):
        self.exibicao.update_display(self.state, self._fmt(self.remaining))

    # ===== Atalhos de teclado =====
    def keyPressEvent(self, event):  # type: ignore
        key = event.key()
        if key == Qt.Key_Space:  # type: ignore
            self.pause() if self.running else self.start()
        elif key == Qt.Key_T:  # type: ignore
            self.reset()
        elif key == Qt.Key_R:  # type: ignore
            self.reset_all()
        elif key == Qt.Key_F11:  # type: ignore
            self.exibicao.toggle_fullscreen()
        elif key == Qt.Key_P:  # type: ignore
            self.pause()
        elif key == Qt.Key_I:  # type: ignore
            self.start()


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
        atleta1 = self.atleta1_input.text().strip() or ""
        atleta2 = self.atleta2_input.text().strip() or ""
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
