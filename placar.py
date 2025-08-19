import sys
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QLineEdit
)
from PyQt5.QtCore import QTimer, Qt


class PlacarJiuJitsu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Placar de Jiu-Jitsu")
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet("background-color: #111; color: #000;")

        # Estado
        self.state = {
            'A': {'points': 0, 'advantages': 0, 'penalties': 0},
            'B': {'points': 0, 'advantages': 0, 'penalties': 0}
        }

        # Referências dos labels
        self.labels = {'A': {}, 'B': {}}

        # Timer
        self.initial_secs = 5 * 60  # padrão 5 min
        self.remaining = self.initial_secs
        self.running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        # Layout principal
        main = QVBoxLayout(self)

        # ---------- Cronômetro ----------
        self.timer_label = QLabel(self._fmt(self.remaining))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("background:#000; font-size:80px; color:#00ff00; font-weight:900;")
        self.timer_label.setFixedHeight(120)
        main.addWidget(self.timer_label)

        # Entrada para tempo de luta
        time_setter = QHBoxLayout()
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Tempo (min)")
        self.time_input.setFixedWidth(120)  # largura menor
        self.time_input.setFixedHeight(40)  # altura menor
        self.time_input.setStyleSheet("""
            font-size:18px; 
            padding:4px; 
            background:#ddd; 
            color:#000; 
            border-radius:6px;
        """)

        btn_set_time = QPushButton("Definir Tempo")
        btn_set_time.setStyleSheet("""
            font-size:18px; 
            background:#333; 
            color:white; 
            border-radius:6px; 
            padding:6px 12px;
        """)
        btn_set_time.clicked.connect(self.set_time)

        time_setter.addWidget(self.time_input)
        time_setter.addWidget(btn_set_time)
        main.addLayout(time_setter)


        # ---------- Área dos atletas ----------
        board = QHBoxLayout()
        board.addWidget(self._build_side("A", "ATLETA 1", "white"))
        board.addWidget(self._build_side("B", "ATLETA 2", "#199649"))
        main.addLayout(board)

        # Controles do cronômetro
        timer_controls = QHBoxLayout()
        for text, func in [("▶ Iniciar", self.start), ("⏸ Pausar", self.pause), ("⏹ Resetar", self.reset)]:
            btn = QPushButton(text)
            btn.setStyleSheet("font-size:22px; padding:12px; background:#333; color:white; border-radius:10px;")
            btn.clicked.connect(func)
            timer_controls.addWidget(btn)
        main.addLayout(timer_controls)

    # ---------- Bloco de cada atleta ----------
    def _build_side(self, side, name, color):
        frame = QFrame()
        frame.setStyleSheet(f"background:{color}; border:2px solid #000;")
        layout = QVBoxLayout(frame)

        # Nome
        name_lbl = QLabel(name)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet("""
            font-size:32px; 
            font-weight:700; 
            background: transparent;
            border: none;
            color:black;
        """)
        layout.addWidget(name_lbl)

        # Pontos
        self.labels[side]['points'] = QLabel("0")
        self.labels[side]['points'].setAlignment(Qt.AlignCenter)
        self.labels[side]['points'].setStyleSheet("font-size:300px; font-weight:900; color:black; border: none")
        layout.addWidget(self.labels[side]['points'])

        # Penalidade e Vantagem
        bottom = QHBoxLayout()

        # Penalidade
        pen_frame = QFrame()
        pen_frame.setStyleSheet("background:red; border:2px solid transparent;")
        pen_layout = QVBoxLayout(pen_frame)
        pen_lbl = QLabel("PENALIDADE")
        pen_lbl.setAlignment(Qt.AlignCenter)
        pen_lbl.setStyleSheet("font-size:24px; font-weight:bold; color:black;")
        self.labels[side]['penalties'] = QLabel("0")
        self.labels[side]['penalties'].setAlignment(Qt.AlignCenter)
        self.labels[side]['penalties'].setStyleSheet("font-size:50px; font-weight:900; color:black;")
        pen_layout.addWidget(pen_lbl)
        pen_layout.addWidget(self.labels[side]['penalties'])
        # Botões penalidade
        pen_btns = QHBoxLayout()
        for t, v in [("+", 1), ("−", -1)]:
            b = QPushButton(t)
            b.setStyleSheet("font-size:20px; background:#333; color:white; border-radius:8px;")
            b.clicked.connect(partial(self._change, side, "penalties", v))
            pen_btns.addWidget(b)
        pen_layout.addLayout(pen_btns)

        # Vantagem
        vant_frame = QFrame()
        vant_frame.setStyleSheet("background:#0181ba; border:2px solid transparent;")
        vant_layout = QVBoxLayout(vant_frame)
        vant_lbl = QLabel("VANTAGEM")
        vant_lbl.setAlignment(Qt.AlignCenter)
        vant_lbl.setStyleSheet("font-size:24px; font-weight:bold; color:black;")
        self.labels[side]['advantages'] = QLabel("0")
        self.labels[side]['advantages'].setAlignment(Qt.AlignCenter)
        self.labels[side]['advantages'].setStyleSheet("font-size:50px; font-weight:900; color:black;")
        vant_layout.addWidget(vant_lbl)
        vant_layout.addWidget(self.labels[side]['advantages'])
        # Botões vantagem
        vant_btns = QHBoxLayout()
        for t, v in [("+", 1), ("−", -1)]:
            b = QPushButton(t)
            b.setStyleSheet("font-size:20px; background:#333; color:white; border-radius:8px;")
            b.clicked.connect(partial(self._change, side, "advantages", v))
            vant_btns.addWidget(b)
        vant_layout.addLayout(vant_btns)

        bottom.addWidget(pen_frame)
        bottom.addWidget(vant_frame)
        layout.addLayout(bottom)

        # Botões de pontos
        pts_layout = QHBoxLayout()
        for label, val in [("Queda/Raspagem +2", 2), ("Passagem +3", 3), ("Montada/Costas +4", 4), ("−1 ponto", -1)]:
            b = QPushButton(label)
            b.setStyleSheet("font-size:20px; padding:10px; background:#444; color:white; border-radius:10px;")
            b.clicked.connect(partial(self._change, side, "points", val))
            pts_layout.addWidget(b)
        layout.addLayout(pts_layout)

        return frame

    # ---------- Atualização dos valores ----------
    def _change(self, side, metric, delta):
        new_val = max(0, self.state[side][metric] + delta)
        self.state[side][metric] = new_val
        self.labels[side][metric].setText(str(new_val))

    # ---------- Timer ----------
    def _fmt(self, s):
        m, sec = divmod(int(s), 60)
        return f"{m:02}:{sec:02}"

    def _tick(self):
        if not self.running:
            return
        if self.remaining > 0:
            self.remaining -= 1
            self.timer_label.setText(self._fmt(self.remaining))
        if self.remaining <= 0:
            self.running = False
            self.timer.stop()

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

    def set_time(self):
        try:
            minutes = int(self.time_input.text())
            self.initial_secs = minutes * 60
            self.reset()
        except ValueError:
            self.time_input.setText("Erro: digite número")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlacarJiuJitsu()
    w.showMaximized()  # já abre maximizado (bom para telão)
    sys.exit(app.exec_())
