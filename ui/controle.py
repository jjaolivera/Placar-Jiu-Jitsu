import sys
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QShortcut, QSpinBox, QMessageBox,)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import QTimer, Qt

from ui.exibicao import PlacarExibicao

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
