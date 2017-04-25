import kivy

import itertools
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from kivy.uix.spinner import Spinner

from kivy.graphics import Rectangle, Color, Canvas
from functools import partial
from random import randint
from kivy.resources import resource_add_path
from kivy.resources import resource_find
import time
import os
import thread
from kivy.config import Config

pls_wait_for_real = False

def waitpls():
    global pls_wait_for_real
    time.sleep(0.6)
    pls_wait_for_real = False

dir_path = os.path.dirname(os.path.realpath(__file__))

resource_add_path('C:/Users/aseryz/Desktop/Nastya/AGH/OOPL/Memory game/Source/Classic/')

Config.set('graphics', 'resizable', True)  # don't make the app re-sizeable
Window.clearcolor = (1, 1, 1, 1)
Window.size = (1000, 800)


class Menu(Widget):
    buttonList = []
    done = False
    def __init__(self, **kwargs):
        # create custom events first
        self.register_event_type('on_button_release')

        super(Menu, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.width = Window.width / 2
        self.layout.height = Window.height / 2
        self.layout.x = Window.width / 2 - self.layout.width / 2
        self.layout.y = Window.height / 2 - self.layout.height / 2
        self.add_widget(self.layout)

    def on_button_release(self, *args):
        print 'The on_button_release event was just dispatched', args
        # don't need to do anything here. needed for dispatch
        pass

    def callback(self, instance):
        print('The button %s is being pressed' % instance.text)
        self.buttonText = instance.text
        self.dispatch('on_button_release')

    def addButtons(self):
        for k in self.buttonList:
            tmpBtn = Button(text=k)
            tmpBtn.background_color = [.4, .4, .4, .4]
            tmpBtn.bind(on_release=self.callback)  # when the button is released the callback function is called
            self.layout.add_widget(tmpBtn)

    def buildUp(self):
        if not self.done:
            self.addButtons()
            self.done = True

class StartMenu(Menu):
    # setup the menu button names
    buttonList = ['Start', 'Settings', 'Exit']

    def __init__(self, **kwargs):
        super(StartMenu, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.width = Window.width / 2
        self.layout.height = Window.height / 2
        self.layout.x = Window.width / 2 - self.layout.width / 2
        self.layout.y = Window.height / 2 - self.layout.height / 2
        self.add_widget(self.layout)

        self.msg = Label(text='Memory game')
        self.msg.color = (0, 0, 0, 1)
        self.msg.font_size = Window.width * 0.07
        self.msg.pos = (Window.width * 0.45, Window.height * 0.75)
        self.add_widget(self.msg)

class LevelMenu(Menu):
    # setup the menu button names
    buttonList = ['Easy', 'Medium', 'Hard', 'Custom', 'Cancel']

    def __init__(self, **kwargs):
        super(LevelMenu, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.width = Window.width / 2
        self.layout.height = Window.height / 2
        self.layout.x = Window.width / 2 - self.layout.width / 2
        self.layout.y = Window.height / 2 - self.layout.height / 2
        self.add_widget(self.layout)

        self.msg = Label(text='Memory game')
        self.msg.color = (0, 0, 0, 1)
        self.msg.font_size = Window.width * 0.07
        self.msg.pos = (Window.width * 0.45, Window.height * 0.75)
        self.add_widget(self.msg)


class CustomLevel(Menu):
    buttonList = ['Ok','Cancel']

    def __init__(self, **kwargs):
        super(CustomLevel, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.width = Window.width / 2
        self.layout.height = Window.height / 2
        self.layout.x = Window.width / 2 - self.layout.width / 2
        self.layout.y = Window.height / 2 - self.layout.height / 2
        self.add_widget(self.layout)
        self.custom_row=None
        self.custom_column=None

        def selected_value_r(spinner_row, text):
            print 'Cust Value:%s' % text
            self.number = int(text)
            print 'Cust Num:%s' % self.number
            self.custom_row = self.number

        def selected_value_c(spinner_column, text):
            print 'Cust Value:%s' % text
            self.number = int(text)
            print 'Cust Num:%s' % self.number
            self.custom_column = self.number

        self.spinner_row=Spinner(text='Number of Rows',values=('2','4','6'))
        self.spinner_row.bind(text=selected_value_r)
        self.layout.add_widget(self.spinner_row)

        self.spinner_column = Spinner(text='Number of Columns',values=('1','3','5'))
        self.spinner_column.bind(text=selected_value_c)
        # self.spinner_column.bind(text=self.spinner_column.selected_value)
        # self.custom_column = self.spinner_column.selected_value
        self.layout.add_widget(self.spinner_column)

        self.msg = Label(text='Memory game')
        self.msg.color = (0, 0, 0, 1)
        self.msg.font_size = Window.width * 0.07
        self.msg.pos = (Window.width * 0.45, Window.height * 0.75)
        self.add_widget(self.msg)


class Card(ButtonBehavior, Image):

    coords = ListProperty([0, 0])
    card_pos_x = 0
    card_pos_y = 0

    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)
        # self.background_color=(255,255,255)
        # os.path.join(dir_path, 'Car')
        self.source = 'C:/Users/aseryz/Desktop/Nastya/AGH/OOPL/Memory game/Source/Card-Back-01.png'
        self.allow_stretch = True
        self.keep_ratio = True
        self.flipped = False
        self.card_rank=None
        self.card_suit=None

    def set_card_rand(self, card_rank,card_suit):
        self.card_rank = card_rank
        self.card_suit = card_suit

    def get_card_suit(self):
       return self.card_suit

    def get_card_rank(self):
        return self.card_rank

    def set_source_face(self,face):
        self.face=resource_find(face)
        # self.face=resource_find('Classic/c01.png')
        print self.face
        return self.face

    def set_source_back(self):
        self.back = 'C:/Users/aseryz/Desktop/Nastya/AGH/OOPL/Memory game/Source/Card-Back-01.png'
        return self.back

    def flip(self):
        if not self.flipped:
            self.source=self.set_source_face(self.face)
            print 'I changed to face'
            self.reload()

        else:
            self.source=self.set_source_back()
            print 'I changed to back.'
            self.reload()

        self.flipped= not self.flipped
        print self.flipped
        self.reload()

    def get_flipped_state(self):

        return self.flipped


class CardDesk(GridLayout):
    def __init__(self, **kwargs):
        super(CardDesk, self).__init__(**kwargs)

        self.tmpCard=None
        self.card_stack=[]
        self.game_state=1
        self.game_over=0
        self.flipping=False

        self.register_event_type('on_card_release')

        self.width = Window.width
        self.height = Window.height
        self.x = Window.width - self.width
        self.y = Window.height - self.height
        self.cardList = None
        self.spacing = [50, 20]

    def set_bounds(self, ip_rows, ip_cols):
        self.rows = ip_rows
        self.cols = ip_cols
        self.cardList = None
        self.cardList = range(ip_rows * ip_cols)
        print 'Card list:%s' % self.cardList

    def randomize_cards(self):

        self.rand_r=None
        self.rand_s=None
        t=0
        p=0
        print 't:%s' % t

        self.rand_r = randint(1, 13)
        print 'Rand R:%s' % self.rand_r

        self.rand_s = randint(0, 3)
        print 'Rand S:%s' % self.rand_s

        self.card_stack[t].set_card_rand(self.rand_r, self.rand_s)
        p=randint(1,(self.rows*self.cols)-1)
        print 'p:%s' %p

        self.card_stack[p].set_card_rand(self.rand_r, self.rand_s)

        for i in itertools.islice(self.cardList,0,((self.rows*self.cols)/2)-1):

            self.rand_r = randint(1, 13)
            print 'Rand R:%s' %self.rand_r

            self.rand_s = randint(0, 3)
            print 'Rand S:%s' % self.rand_s

            p = randint(1, (self.rows * self.cols))
            print 'i:%s p:%s' % (i,p)

            while self.card_stack[t].get_card_rank()!=None:
                if t==(self.rows*self.cols)-1:
                    t=1
                else:
                    t+=1
            self.card_stack[t].set_card_rand(self.rand_r,self.rand_s)

            t=randint(0,(self.rows*self.cols)-2)+1
            while self.card_stack[t].get_card_rank()!=None:
                if t==(self.rows*self.cols)-1:
                    t=1
                else:
                    t+=1
            self.card_stack[t].set_card_rand(self.rand_r,self.rand_s)
            t = randint(0, (self.rows*self.cols) - 2) +1


    def on_card_release(self,*args):
        print 'The on_card_release event was just dispatched', args
        # don't need to do anything here. needed for dispatch


    def callback(self, instance ):

        global pls_wait_for_real

        if not self.flipping:
            self.flipping=True

            if self.game_state==1 and not pls_wait_for_real:
                self.game_state=2
                print ('The card r/c:{}  is being pressed'.format(instance.coords))
                instance.card_pos_y, instance.card_pos_x = instance.coords
                self.flip_card(instance.card_pos_y, instance.card_pos_x)
                self.flipped_card_col=instance.card_pos_x
                self.flipped_card_row=instance.card_pos_y
                self.flipped_card_rank=self.card_stack[
                    instance.card_pos_y*self.cols+instance.card_pos_x].get_card_rank()
                self.flipped_card_suit = self.card_stack[
                    instance.card_pos_y * self.cols + instance.card_pos_x].get_card_suit()

                self.card_stack[self.flipped_card_row * self.cols + self.flipped_card_col].disabled=True

            elif self.game_state==2:

                pls_wait_for_real = True
                thread.start_new(waitpls,())

                print ('The card 2 r/c:{}  is being pressed'.format(instance.coords))

                instance.card_pos_y, instance.card_pos_x = instance.coords

                self.flip_card(instance.card_pos_y, instance.card_pos_x)

                self.card_stack[instance.card_pos_y * self.cols + instance.card_pos_x].disabled = True

                print 'Card 2 Disabled?:%s' %self.card_stack[instance.card_pos_y * self.cols + instance.card_pos_x].disabled

                if self.flipped_card_rank==self.card_stack[
                    instance.card_pos_y*self.cols+instance.card_pos_x].get_card_rank() and self.flipped_card_suit==self.card_stack[
                    instance.card_pos_y * self.cols + instance.card_pos_x].get_card_suit():

                    self.game_over=self.check_flipped_cards()
                    if self.game_over==1:
                        self.remove()
                        print 'Game Over!'
                else:

                    Clock.schedule_once(lambda dt:self.flip_card(instance.card_pos_y, instance.card_pos_x),0.5)
                    Clock.schedule_once(lambda dt: self.flip_card(self.flipped_card_row, self.flipped_card_col), 0.5)

                    self.card_stack[instance.card_pos_y * self.cols + instance.card_pos_x].disabled = False
                    self.card_stack[self.flipped_card_row * self.cols + self.flipped_card_col].disabled = False

                self.game_state=1
            self.flipping=False
        self.dispatch('on_card_release')

    def addCards(self):
        for row in range(self.rows):
            for column in range(self.cols):
                self.tmpCard = Card(coords=(row, column), card_pos_x=column, card_pos_y=row)
                self.tmpCard.bind(on_release=self.callback)
                self.card_stack.append(self.tmpCard)
                self.add_widget(self.tmpCard)
        self.randomize_cards()
        for row in range(self.rows):
            for column in range(self.cols):
                source=str(self.card_stack[row *self.cols+column].get_card_suit())+\
                       str((self.card_stack[row *self.cols+column].get_card_rank()))+'.png'
                print 'Card suit:%s rank:%s' % (
                self.card_stack[row *self.cols+column].get_card_suit(), self.card_stack[row *self.cols+column].get_card_rank())
                print 'Source: %s' % source
                self.card_stack[row * self.cols + column].set_source_face(str(source))

    def buildUp(self):
        self.addCards()

    def remove(self):
        for row in range(self.rows):
            for column in range(self.cols):
                    self.remove_widget(self.card_stack[row *self.cols+column])

    def flip_card(self,fl_row,fl_col):
        self.card_stack[fl_row*self.cols+fl_col].flip()
        print 'I flipped!! r:%s c:%s' %(fl_row,fl_col)

    def check_flipped_cards(self):
        for row in range(self.rows):
            for column in range(self.cols):
                if not self.card_stack[row *self.cols+column].get_flipped_state():
                    return 0
        return 1


class ClientApp(App):
    def build(self):

        self.parent = Widget()

        self.sm = StartMenu()
        self.sm.buildUp()

        self.lm = LevelMenu()
        self.cl=CustomLevel()

        def check_custlevel_button(obj):

            if self.cl.buttonText == 'Ok':

                self.de = CardDesk()

                self.de.set_bounds(self.cl.custom_row,self.cl.custom_column)
                self.de.buildUp()
                self.parent.remove_widget(self.cl)
                self.parent.add_widget(self.de)
                print ' we should start the game now custom'

            if self.cl.buttonText == 'Cancel':
                self.parent.remove_widget(self.cl)
                self.parent.add_widget(self.sm)
                print 'Cancel'

        def check_level_button(obj):

            if self.lm.buttonText == 'Easy':
                self.parent.remove_widget(self.lm)
                self.de = CardDesk()
                self.de.set_bounds(3, 4)
                self.de.buildUp()
                self.parent.add_widget(self.de)
                print ' we should start the game now easy'

            if self.lm.buttonText == 'Medium':
                self.parent.remove_widget(self.lm)
                self.de = CardDesk()
                self.de.set_bounds(4, 5)
                self.de.buildUp()
                self.parent.add_widget(self.de)
                print ' we should start the game now medium'

            if self.lm.buttonText == 'Hard':
                self.parent.remove_widget(self.lm)
                self.de = CardDesk()
                self.de.set_bounds(5, 6)
                self.de.buildUp()
                self.parent.add_widget(self.de)
                print ' we should start the game now hard'

            if self.lm.buttonText == 'Custom':
                self.parent.remove_widget(self.lm)
                self.parent.add_widget(self.cl)
                self.cl.buildUp()
                print ' we should start the game now custom'

            if self.lm.buttonText == 'Cancel':
                self.parent.remove_widget(self.lm)
                self.parent.add_widget(self.sm)
                print 'Cancel'

        def check_start_button(obj):
            # check to see which button was pressed
            if self.sm.buttonText == 'Start':
                self.parent.remove_widget(self.sm)
                self.parent.add_widget(self.lm)
                #if not self.lm.done:
                self.lm.buildUp()
                #self.lm.done = True

            if self.sm.buttonText == 'Settings':
                self.parent.remove_widget(self.sm)
                print ' Score table'

            if self.sm.buttonText == 'Exit':
                self.parent.remove_widget(self.parent)
                App.get_running_app().stop()
                print ' Exit'

        self.sm.bind(on_button_release=check_start_button)
        self.lm.bind(on_button_release=check_level_button)
        self.cl.bind(on_button_release=check_custlevel_button)

        self.parent.add_widget(self.sm)

        return self.parent

if __name__ == '__main__':
    ClientApp().run()
