# main.py - PEAK PREDICTOR EN KIVY

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.utils import get_color_from_hex

import threading
import random
import os
import json
import hashlib
import uuid
import platform
from datetime import datetime, timedelta
from collections import deque

COLORES = {
    'fondo': '#1a1a2e',
    'card': '#16213e',
    'primario': '#0f3460',
    'acento': '#e94560',
    'verde': '#00ff88',
    'rojo': '#ff4444',
    'blanco': '#ffffff',
    'gris': '#888888',
    'amarillo': '#ffaa00',
    'azul': '#0066ff'
}

class LicenseManager:
    def __init__(self):
        self.hwid = self.get_or_create_hwid()
        self.licencia_file = "licencia.lic"
        self.trial_file = "trial.json"
        self.validated = False
        self.license_data = None
        self.secret = "PREDICTOR_SECRET_2026"
        self.is_trial = False
        self.trial_duration_hours = 24

    def get_or_create_hwid(self):
        hwid_file = "hwid.txt"
        if os.path.exists(hwid_file):
            try:
                with open(hwid_file, 'r') as f:
                    hwid = f.read().strip()
                    if hwid:
                        return hwid
            except:
                pass
        hwid = self.generar_hwid()
        try:
            with open(hwid_file, 'w') as f:
                f.write(hwid)
        except:
            pass
        return hwid

    def generar_hwid(self):
        try:
            data = []
            mac = uuid.getnode()
            data.append(str(mac))
            hostname = platform.node()
            data.append(hostname)
            data.append(platform.system())
            data.append(platform.release())
            combined = "".join(data)
            return hashlib.sha256(combined.encode()).hexdigest()
        except:
            return str(uuid.uuid4())

    def activar_trial(self):
        try:
            now = datetime.now()
            expiry = now + timedelta(hours=self.trial_duration_hours)
            trial_data = {
                "hwid": self.hwid,
                "start": now.isoformat(),
                "expiry": expiry.isoformat(),
                "trial": True
            }
            with open(self.trial_file, 'w') as f:
                json.dump(trial_data, f, indent=2)
            self.is_trial = True
            self.validated = True
            self.license_data = trial_data
            return True, f"Prueba activada por {self.trial_duration_hours} horas"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_trial(self):
        if not os.path.exists(self.trial_file):
            return False, "No hay prueba activa"
        try:
            with open(self.trial_file, 'r') as f:
                data = json.load(f)
            if data.get('hwid') != self.hwid:
                return False, "Prueba para otro dispositivo"
            expiry = datetime.fromisoformat(data.get('expiry', ''))
            if expiry < datetime.now():
                os.remove(self.trial_file)
                return False, "Prueba expirada"
            self.is_trial = True
            self.validated = True
            self.license_data = data
            hours = int((expiry - datetime.now()).total_seconds() / 3600)
            return True, f"Prueba - {hours}h restantes"
        except:
            return False, "Error al verificar prueba"

    def check_activation(self):
        if self.validated and self.license_data and not self.is_trial:
            expiry = self.license_data.get('expiry', '')
            if expiry == "9999-12-31":
                return True, "Permanente"
            else:
                try:
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
                    if expiry_date > datetime.now():
                        return True, f"Valida hasta {expiry}"
                    else:
                        self.validated = False
                        self.license_data = None
                except:
                    pass
        if os.path.exists(self.licencia_file):
            try:
                with open(self.licencia_file, 'r') as f:
                    licencia = json.load(f)
                if licencia.get('hwid') != self.hwid:
                    return False, "Licencia para otro dispositivo"
                data = f"{licencia['hwid']}{licencia['expiry']}{licencia['id']}{self.secret}"
                if hashlib.sha256(data.encode()).hexdigest() != licencia.get('hash'):
                    return False, "Licencia corrupta"
                expiry = licencia.get('expiry', '')
                if expiry != "9999-12-31":
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
                    if expiry_date < datetime.now():
                        return False, f"Licencia expirada el {expiry}"
                self.validated = True
                self.license_data = licencia
                self.is_trial = False
                return True, f"Licencia valida - {licencia.get('duracion', '')}"
            except:
                pass
        trial_valid, trial_msg = self.check_trial()
        if trial_valid:
            return True, trial_msg
        return False, "No activado"

    def get_hwid_display(self):
        return self.hwid

class BettingAccount:
    def __init__(self, username, password, account_id):
        self.username = username
        self.password = password
        self.account_id = account_id
        self.balance = 100.0
        self.is_logged_in = False
        self.current_bet = 0.1
        self.consecutive_losses = 0

    def login(self):
        self.is_logged_in = True
        return True, f"OK {self.username}: ${self.balance:.2f}"

class BettingSystem:
    def __init__(self):
        self.accounts = []

    def add_account(self, username, password):
        if len(self.accounts) >= 3:
            return False, "Maximo 3 cuentas"
        for acc in self.accounts:
            if acc.username == username:
                return False, "La cuenta ya existe"
        account_id = len(self.accounts) + 1
        account = BettingAccount(username, password, account_id)
        self.accounts.append(account)
        return True, f"Cuenta {account_id}: {username} agregada"

    def login_all(self):
        results = []
        for account in self.accounts:
            success, message = account.login()
            results.append(message)
        return results

    def get_active_accounts(self):
        return [acc for acc in self.accounts if acc.is_logged_in]

    def get_total_balance(self):
        return sum(account.balance for account in self.accounts if account.is_logged_in)

class TrendFollowerPredictor:
    def __init__(self):
        self.reset_session()

    def reset_session(self):
        self.session_history = deque(maxlen=30)
        self.last_prediction = None
        self.consecutive_losses = 0
        self.max_losses = 3
        self.modo_alternancia = False
        self.break_detected = False
        self.last_colors_display = []

    def process_color(self, new_color):
        if new_color not in ['red', 'blue']:
            return
        self.session_history.append(new_color)
        self.last_colors_display = list(self.session_history)[-6:]
        if self.modo_alternancia:
            self.detect_break()

    def detect_break(self):
        if len(self.session_history) < 4:
            return
        last_4 = list(self.session_history)[-4:]
        if last_4[0] == last_4[1] or last_4[1] == last_4[2] or last_4[2] == last_4[3]:
            self.modo_alternancia = False
            self.break_detected = True
            self.consecutive_losses = 0

    def update_prediction(self, actual_color):
        was_correct = self.last_prediction == actual_color
        if was_correct:
            self.consecutive_losses = 0
            self.modo_alternancia = False
            self.break_detected = False
        else:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.max_losses:
                self.modo_alternancia = True
                self.break_detected = False
        return was_correct

    def get_prediction(self):
        if not self.session_history:
            return None, 0.0, "Esperando datos..."
        if self.modo_alternancia:
            return None, 0.0, "ALTERNANCIA - Esperando ruptura..."
        last_color = self.session_history[-1]
        confidence = 0.75
        if len(self.session_history) >= 2:
            last_two = list(self.session_history)[-2:]
            if last_two[0] == last_two[1]:
                confidence = 0.85
        return last_color, confidence, f"Seguir: {last_color.upper()} ({int(confidence*100)}%)"

class PeakScreen(Screen):
    def __init__(self, **kwargs):
        super(PeakScreen, self).__init__(**kwargs)
        self.license_manager = LicenseManager()
        self.predictor = TrendFollowerPredictor()
        self.betting_system = BettingSystem()
        self.running = False
        self.betting_active = False
        self.wins = 0
        self.losses = 0
        self.prediction_index = 0

        self.build_ui()
        self.check_activation()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=8)

        titulo = Label(text="PEAK PREDICTOR", font_size=28, bold=True,
                       color=get_color_from_hex(COLORES['acento']),
                       size_hint_y=None, height=40)
        layout.add_widget(titulo)

        self.status_label = Label(text="Verificando licencia...", font_size=14,
                                  color=get_color_from_hex(COLORES['blanco']),
                                  size_hint_y=None, height=25)
        layout.add_widget(self.status_label)

        tabs = TabbedPanel(do_default_tab=False, size_hint_y=None, height=430)

        tab1 = TabbedPanelItem(text="Principal")
        tab1_content = self.build_tab_principal()
        tab1.add_widget(tab1_content)
        tabs.add_widget(tab1)

        tab2 = TabbedPanelItem(text="Cuentas")
        tab2_content = self.build_tab_cuentas()
        tab2.add_widget(tab2_content)
        tabs.add_widget(tab2)

        layout.add_widget(tabs)

        console_label = Label(text="Log", font_size=13, bold=True,
                              color=get_color_from_hex(COLORES['blanco']),
                              size_hint_y=None, height=20)
        layout.add_widget(console_label)

        self.console = TextInput(text="", font_size=10, multiline=True,
                                 background_color=get_color_from_hex(COLORES['card']),
                                 foreground_color=get_color_from_hex(COLORES['blanco']),
                                 size_hint_y=0.25)
        layout.add_widget(self.console)

        scroll = ScrollView()
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def build_tab_principal(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        hwid_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
        hwid_box.add_widget(Label(text="ID:", font_size=12,
                                  color=get_color_from_hex(COLORES['blanco']),
                                  size_hint_x=0.15))
        self.hwid_text = TextInput(text=self.license_manager.get_hwid_display()[:20] + "...",
                                   font_size=11, readonly=True,
                                   background_color=get_color_from_hex(COLORES['card']),
                                   foreground_color=get_color_from_hex(COLORES['blanco']))
        hwid_box.add_widget(self.hwid_text)
        layout.add_widget(hwid_box)

        btn_lic = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=8)
        self.btn_trial = Button(text="PRUEBA 24h",
                                background_color=get_color_from_hex(COLORES['primario']),
                                color=get_color_from_hex(COLORES['blanco']))
        self.btn_trial.bind(on_press=self.activar_trial)
        btn_lic.add_widget(self.btn_trial)

        self.btn_verify = Button(text="VERIFICAR",
                                 background_color=get_color_from_hex(COLORES['acento']),
                                 color=get_color_from_hex(COLORES['blanco']))
        self.btn_verify.bind(on_press=self.verificar_licencia)
        btn_lic.add_widget(self.btn_verify)
        layout.add_widget(btn_lic)

        self.mode_label = Label(text="ESPERANDO", font_size=14, bold=True,
                                color=get_color_from_hex(COLORES['gris']),
                                size_hint_y=None, height=25)
        layout.add_widget(self.mode_label)

        self.loss_label = Label(text="Perdidas: 0/3", font_size=13,
                                color=get_color_from_hex(COLORES['blanco']),
                                size_hint_y=None, height=25)
        layout.add_widget(self.loss_label)

        color_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        color_box.add_widget(Label(text="Ultimos:",
                                   color=get_color_from_hex(COLORES['blanco']),
                                   font_size=12, size_hint_x=0.2))
        self.color_canvas = BoxLayout(orientation='horizontal', size_hint_x=0.8)
        color_box.add_widget(self.color_canvas)
        layout.add_widget(color_box)

        pred_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        pred_box.add_widget(Label(text="Prediccion:",
                                  color=get_color_from_hex(COLORES['blanco']),
                                  font_size=14, size_hint_x=0.3))
        self.pred_label = Label(text="Esperando...", font_size=16, bold=True,
                                color=get_color_from_hex(COLORES['gris']))
        pred_box.add_widget(self.pred_label)
        layout.add_widget(pred_box)

        conf_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        conf_box.add_widget(Label(text="Confianza:",
                                  color=get_color_from_hex(COLORES['blanco']),
                                  font_size=12, size_hint_x=0.3))
        self.conf_label = Label(text="0%", font_size=14, bold=True,
                                color=get_color_from_hex(COLORES['blanco']))
        conf_box.add_widget(self.conf_label)
        layout.add_widget(conf_box)

        stats_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.wins_label = Label(text="Wins: 0",
                                color=get_color_from_hex(COLORES['verde']),
                                font_size=12)
        stats_box.add_widget(self.wins_label)
        self.losses_label = Label(text="Losses: 0",
                                  color=get_color_from_hex(COLORES['rojo']),
                                  font_size=12)
        stats_box.add_widget(self.losses_label)
        layout.add_widget(stats_box)

        self.btn_start = Button(text="INICIAR", size_hint_y=None, height=45,
                                background_color=get_color_from_hex(COLORES['verde']),
                                color=get_color_from_hex(COLORES['fondo']))
        self.btn_start.bind(on_press=self.toggle_session)
        layout.add_widget(self.btn_start)

        self.btn_betting = Button(text="AUTO BET", size_hint_y=None, height=40,
                                  background_color=get_color_from_hex(COLORES['primario']),
                                  color=get_color_from_hex(COLORES['blanco']),
                                  disabled=True)
        self.btn_betting.bind(on_press=self.toggle_auto_betting)
        layout.add_widget(self.btn_betting)

        return layout

    def build_tab_cuentas(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        add_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
        self.user_input = TextInput(hint_text="Usuario", font_size=11,
                                    background_color=get_color_from_hex(COLORES['card']),
                                    foreground_color=get_color_from_hex(COLORES['blanco']),
                                    size_hint_x=0.35)
        add_box.add_widget(self.user_input)
        self.pass_input = TextInput(hint_text="Password", font_size=11,
                                    background_color=get_color_from_hex(COLORES['card']),
                                    foreground_color=get_color_from_hex(COLORES['blanco']),
                                    password=True, size_hint_x=0.35)
        add_box.add_widget(self.pass_input)
        self.btn_add = Button(text="+", size_hint_x=0.15,
                              background_color=get_color_from_hex(COLORES['verde']),
                              color=get_color_from_hex(COLORES['fondo']))
        self.btn_add.bind(on_press=self.add_account)
        add_box.add_widget(self.btn_add)
        self.btn_login_all = Button(text="LOGIN", size_hint_x=0.15,
                                    background_color=get_color_from_hex(COLORES['primario']),
                                    color=get_color_from_hex(COLORES['blanco']))
        self.btn_login_all.bind(on_press=self.login_all_accounts)
        add_box.add_widget(self.btn_login_all)
        layout.add_widget(add_box)

        self.cuentas_box = BoxLayout(orientation='vertical', size_hint_y=0.4)
        layout.add_widget(self.cuentas_box)

        total_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        self.total_balance_label = Label(text="Total: $0.00",
                                         color=get_color_from_hex(COLORES['blanco']),
                                         font_size=12)
        total_box.add_widget(self.total_balance_label)
        layout.add_widget(total_box)

        return layout

    def check_activation(self):
        valid, msg = self.license_manager.check_activation()
        if valid:
            self.status_label.text = f"OK - {msg}"
            self.status_label.color = get_color_from_hex(COLORES['verde'])
            self.btn_verify.text = "ACTIVADO"
            self.btn_verify.background_color = get_color_from_hex(COLORES['verde'])
            self.btn_trial.disabled = True
        else:
            self.status_label.text = f"NO - {msg}"
            self.status_label.color = get_color_from_hex(COLORES['rojo'])

    def activar_trial(self, instance):
        success, msg = self.license_manager.activar_trial()
        if success:
            self.status_label.text = f"OK - {msg}"
            self.status_label.color = get_color_from_hex(COLORES['verde'])
            self.btn_verify.text = "ACTIVADO"
            self.btn_verify.background_color = get_color_from_hex(COLORES['verde'])
            self.btn_trial.disabled = True
            self.log(f"OK: {msg}")
        else:
            self.log(f"ERROR: {msg}")

    def verificar_licencia(self, instance):
        valid, msg = self.license_manager.check_activation()
        if valid:
            self.status_label.text = f"OK - {msg}"
            self.status_label.color = get_color_from_hex(COLORES['verde'])
            self.btn_verify.text = "ACTIVADO"
            self.btn_verify.background_color = get_color_from_hex(COLORES['verde'])
            self.log(f"OK: {msg}")
        else:
            self.status_label.text = f"NO - {msg}"
            self.status_label.color = get_color_from_hex(COLORES['rojo'])
            self.log(f"ERROR: {msg}")
            if "expirada" in msg.lower():
                self.log("Contacte a @LixoTrader para activar su licencia")

    def add_account(self, instance):
        username = self.user_input.text.strip()
        password = self.pass_input.text.strip()
        if not username or not password:
            self.log("ERROR: Ingresa usuario y password")
            return
        success, msg = self.betting_system.add_account(username, password)
        if success:
            self.log(f"OK: {msg}")
            self.user_input.text = ""
            self.pass_input.text = ""
            self.update_cuentas_display()
        else:
            self.log(f"ERROR: {msg}")

    def login_all_accounts(self, instance):
        if len(self.betting_system.accounts) == 0:
            self.log("ERROR: No hay cuentas")
            return
        self.btn_login_all.text = "..."
        self.btn_login_all.disabled = True
        self.log("Iniciando sesion...")

        def thread_login():
            results = self.betting_system.login_all()
            for result in results:
                self.log(result)
            active_count = len(self.betting_system.get_active_accounts())
            if active_count > 0:
                self.log(f"OK: {active_count} cuenta(s) conectada(s)")
                Clock.schedule_once(lambda dt: self.btn_betting.__setattr__('disabled', False), 0)
                self.update_cuentas_display()
            else:
                self.log("ERROR: No se pudo conectar")
            Clock.schedule_once(lambda dt: self.btn_login_all.__setattr__('text', 'LOGIN'), 0)
            Clock.schedule_once(lambda dt: self.btn_login_all.__setattr__('disabled', False), 0)

        threading.Thread(target=thread_login, daemon=True).start()

    def update_cuentas_display(self):
        self.cuentas_box.clear_widgets()
        for account in self.betting_system.accounts:
            status = "ON" if account.is_logged_in else "OFF"
            balance = f"${account.balance:.2f}" if account.is_logged_in else "-"
            label = Label(text=f"{status} {account.username} | {balance}",
                          color=get_color_from_hex(COLORES['blanco']),
                          font_size=12, size_hint_y=None, height=25)
            self.cuentas_box.add_widget(label)
        total_balance = self.betting_system.get_total_balance()
        self.total_balance_label.text = f"Total: ${total_balance:.2f}"

    def toggle_session(self, instance):
        if not self.running:
            self.running = True
            self.btn_start.text = "DETENER"
            self.btn_start.background_color = get_color_from_hex(COLORES['rojo'])
            self.predictor.reset_session()
            self.prediction_index = 0
            self.wins = 0
            self.losses = 0
            self.wins_label.text = "Wins: 0"
            self.losses_label.text = "Losses: 0"
            self.log("Sesion iniciada")
            self.btn_betting.disabled = False
        else:
            self.running = False
            self.btn_start.text = "INICIAR"
            self.btn_start.background_color = get_color_from_hex(COLORES['verde'])
            self.log("Sesion detenida")
            self.btn_betting.disabled = True

    def toggle_auto_betting(self, instance):
        if not self.betting_active:
            self.betting_active = True
            self.btn_betting.text = "STOP BET"
            self.btn_betting.background_color = get_color_from_hex(COLORES['rojo'])
            self.log("Auto Betting activado")
            self.simular_colores()
        else:
            self.betting_active = False
            self.btn_betting.text = "AUTO BET"
            self.btn_betting.background_color = get_color_from_hex(COLORES['primario'])
            self.log("Auto Betting desactivado")

    def simular_colores(self):
        if not self.betting_active:
            return
        colores = ['red', 'blue']
        color = random.choice(colores)
        self.predictor.process_color(color)
        self.color_canvas.clear_widgets()
        for c in self.predictor.last_colors_display:
            bg = get_color_from_hex(COLORES['rojo'] if c == 'red' else COLORES['azul'])
            btn = Button(background_color=bg, size_hint_x=0.15, disabled=True)
            self.color_canvas.add_widget(btn)
        self.log(f"Color: {color.upper()}")
        if self.predictor.last_prediction is not None:
            self.verify_prediction(color)
        else:
            pred, conf, logic = self.predictor.get_prediction()
            if pred:
                self.prediction_index += 1
                self.predictor.last_prediction = pred
                self.pred_label.text = pred.upper()
                self.pred_label.color = get_color_from_hex(
                    COLORES['rojo'] if pred == 'red' else COLORES['azul'])
                self.conf_label.text = f"{int(conf*100)}%"
                self.log(f"Prediccion {self.prediction_index}: {pred.upper()}")
        Clock.schedule_once(lambda dt: self.simular_colores(), 2)

    def verify_prediction(self, actual):
        correct = self.predictor.update_prediction(actual)
        if correct:
            self.wins += 1
            self.wins_label.text = f"Wins: {self.wins}"
            self.log(f"R{self.prediction_index}: {actual.upper()} -> WIN")
            self.mode_label.text = "ACTIVO"
            self.mode_label.color = get_color_from_hex(COLORES['verde'])
            self.loss_label.text = "Perdidas: 0/3"
            self.loss_label.color = get_color_from_hex(COLORES['blanco'])
        else:
            self.losses += 1
            self.losses_label.text = f"Losses: {self.losses}"
            self.log(f"R{self.prediction_index}: {actual.upper()} -> LOSS")
            self.loss_label.text = f"Perdidas: {self.predictor.consecutive_losses}/3"
            if self.predictor.consecutive_losses >= 3:
                self.loss_label.color = get_color_from_hex(COLORES['rojo'])
                self.mode_label.text = "ALTERNANCIA"
                self.mode_label.color = get_color_from_hex(COLORES['amarillo'])
                self.log("3 perdidas - ALTERNANCIA DETECTADA")
            else:
                self.loss_label.color = get_color_from_hex(COLORES['amarillo'])
        self.predictor.last_prediction = None

    def log(self, mensaje):
        self.console.text += f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}\n"
        self.console.cursor = self.console.get_cursor_from_index(len(self.console.text))

class PeakApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex(COLORES['fondo'])
        return PeakScreen()

if __name__ == '__main__':
    PeakApp().run()
