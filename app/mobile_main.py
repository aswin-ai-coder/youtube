from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class YouTubeDownloaderApp(App):
    title = "YouTube Downloader"
    
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='YouTube Downloader', font_size='20sp', size_hint_y=0.1))
        layout.add_widget(Label(text='YouTube URL:', size_hint_y=0.1))
        
        self.url_input = TextInput(multiline=False, hint_text='Paste URL here', size_hint_y=0.15)
        layout.add_widget(self.url_input)
        
        btn = Button(text='Download', size_hint_y=0.15)
        btn.bind(on_press=self.download)
        layout.add_widget(btn)
        
        self.status = Label(text='Ready', size_hint_y=0.3)
        layout.add_widget(self.status)
        
        return layout
    
    def download(self, instance):
        url = self.url_input.text
        if url:
            self.status.text = f'Download started:\n{url}'
        else:
            self.status.text = 'Enter URL first'


if __name__ == '__main__':
    YouTubeDownloaderApp().run()
