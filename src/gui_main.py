import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView

CONFIG_FILE = os.path.expanduser("~/vicious-cli/config/settings.json")
HISTORY_FILE = os.path.expanduser("~/vicious-cli/config/history.json")

class ViciousApp(App):
    def build(self):
        self.title = "Vicious CLI Control Panel"
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # --- Provider Settings Menu ---
        top_bar = BoxLayout(size_hint_y=None, height=40, spacing=10)
        top_bar.add_widget(Label(text="Provider:", size_hint_x=None, width=80))
        
        self.provider_spinner = Spinner(
            text=self.get_current_provider(),
            values=('groq', 'gemini'),
            size_hint_x=None,
            width=120
        )
        self.provider_spinner.bind(text=self.on_provider_change)
        top_bar.add_widget(self.provider_spinner)
        
        main_layout.add_widget(top_bar)
        
        # --- History/Response Viewer ---
        self.history_label = Label(
            text=self.load_history_text(),
            size_hint_y=None,
            markup=True,
            halign='left',
            valign='top'
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.history_label)
        main_layout.add_widget(scroll_view)
        
        # --- Input Bar ---
        input_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.prompt_input = TextInput(hint_text="Ask Vicious or type code...", multiline=False)
        send_btn = Button(text="Send", size_hint_x=None, width=80)
        send_btn.bind(on_press=self.send_prompt)
        
        input_bar.add_widget(self.prompt_input)
        input_bar.add_widget(send_btn)
        main_layout.add_widget(input_bar)
        
        return main_layout

    def get_current_provider(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f).get('provider', 'groq')
        return 'groq'

    def on_provider_change(self, spinner, text):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        data = {'provider': text, 'model': 'openai/gpt-oss-120b' if text == 'groq' else 'gemini-2.5-flash'}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def load_history_text(self):
        if not os.path.exists(HISTORY_FILE):
            return "[b]Vicious Control Panel Ready.[/b]"
        with open(HISTORY_FILE, 'r') as f:
            try:
                data = json.load(f)
                lines = []
                for entry in data[-5:]:
                    lines.append(f"[b]User:[/b] {entry['user']}")
                    lines.append(f"[b]AI:[/b] {entry['assistant']}\n")
                return "\n".join(lines)
            except Exception:
                return "History clear."

    def send_prompt(self, instance):
        prompt = self.prompt_input.text.strip()
        if not prompt:
            return
            
        from ai_chat import generate_ai_response
        response, error = generate_ai_response(prompt)
        
        self.prompt_input.text = ""
        self.history_label.text = self.load_history_text()

if __name__ == '__main__':
    ViciousApp().run()
