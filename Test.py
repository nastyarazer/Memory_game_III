from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

class GameWidget(Widget):
    def start(self):
        return StartMenu()
    def game1(self):
        if StartMenu().pressed_but()==1:
            BoardWidget().desk()
        elif StartMenu().pressed_but()==2:
            pass
        else:
            pass
    def game(self):
        StartMenu().pressed_but()

class BoardWidget(GridLayout):

    def __init__(self, **kwargs):
        super(BoardWidget, self).__init__(**kwargs)
        self.cols = 3
        for i in range(self.cols):
            self.add_widget(Button(text='card'))
    def desk(self):
        self.cols=3
        self.add_widget(Button(text='card'))


class StartMenu(GridLayout):

    def __init__(self, **kwargs):
        super(StartMenu, self).__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(text='Memory game'))
        self.start_but = Button(text='Start')
        self.add_widget(self.start_but)
        self.start_but.bind(on_release=BoardWidget())
        self.score_but=Button(text='Score')
        self.add_widget(self.score_but)
        self.exit_but=Button(text='Exit')
        self.add_widget(self.exit_but)
    def pressed_but(self):
        #self.press = 0
        self.start_but.bind(on_release=BoardWidget().desk())
        #self.score_but.bind(press=2)
        #self.exit_but.bind(press=3)
        #return self.press

class MyApp(App):

    def build(self):
        return  GameWidget().start()


MyApp().run()
