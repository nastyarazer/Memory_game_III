import kivy

import itertools
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from kivy.uix.spinner import Spinner
from random import randint
from kivy.resources import resource_add_path
from kivy.resources import resource_find
import time
import os
import thread
from kivy.config import Config

#Below global variable and function made for holding
#procces of the game for a while.
#Used for wating between turning not mached cards
#and new press from user.
pls_wait_for_real = False

def waitpls():
    global pls_wait_for_real
    time.sleep(0.6)
    pls_wait_for_real = False

#Defining directory path to the main file.
dir_path = os.path.dirname(os.path.realpath(__file__))

#Adding path for application. Used for loading images
#for cards by particular path.
resource_add_path(dir_path)

#Setting configuration for application.
Config.set('graphics', 'resizable', 0)
Window.clearcolor = (1, 1, 1, 1)
Window.resizable=(0)

#Color for all buttons in application.
button_color=[2.1, 0.11, 0.11, 1]

#Menu class inherits class Widget
#Creates an Box with Buttons in the centre of the window.
#Reads events from pressed button.
#Used for creation of all menus in application.
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

        self.msg = Label(text='Memory game')
        self.msg.color = (0, 0, 0, 1)
        self.msg.font_size = Window.width * 0.07
        self.msg.pos = (Window.width * 0.45, Window.height * 0.75)
        self.add_widget(self.msg)

    def on_button_release(self, *args):
        print 'The on_button_release event was just dispatched', args
        # don't need to do anything here. needed for dispatch
        pass

    def callback(self, instance):
        print('The button %s is being pressed' % instance.text)
        self.buttonText = instance.text
        self.dispatch('on_button_release')
#Adding buttons according to the buttonList.
    def addButtons(self):
        for k in self.buttonList:
            tmpBtn = Button(text=k)
            tmpBtn.background_color = button_color
            tmpBtn.bind(on_release=self.callback)  # when the button is released the callback function is called
            self.layout.add_widget(tmpBtn)
#Building all menu widget.
    def buildUp(self):
        if not self.done:
            self.addButtons()
            self.done = True

#Stert menu
class StartMenu(Menu):
    # setup the menu button names
    buttonList = ['Start', 'Exit']
    def __init__(self, **kwargs):
        super(StartMenu, self).__init__(**kwargs)

#Level Menu
class LevelMenu(Menu):
    # setup the menu button names
    buttonList = ['Easy', 'Medium', 'Hard', 'Custom', 'Cancel']

    def __init__(self, **kwargs):
        super(LevelMenu, self).__init__(**kwargs)

#Custom level menu, has the same properties as all menus,
#but has two additional widgets -spiners, for giving
#user a choise which number of rows/columns he wants.
class CustomLevel(Menu):
    buttonList = ['Ok','Cancel']

    def __init__(self, **kwargs):
        super(CustomLevel, self).__init__(**kwargs)

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
        self.layout.add_widget(self.spinner_column)

#Boadr menu has different configuration and placement.
#Placed on the top of the play field with cards.
class BoardMenu(Widget):
    # buttonList = ['Time','Score','Exit']
    buttonList = ['Exit']
    done = False
    def __init__(self, **kwargs):
        # create custom events first
        self.register_event_type('on_button_release')

        super(BoardMenu, self).__init__(**kwargs)

        self.layout=BoxLayout(orientation='horizontal')
        self.layout.width = Window.width
        self.layout.height = Window.height*1/10
        self.layout.x = Window.width-self.layout.width
        self.layout.y = Window.height-self.layout.height
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
            tmpBtn.background_color = button_color
            tmpBtn.bind(on_release=self.callback)  # when the button is released the callback function is called
            self.layout.add_widget(tmpBtn)

    def buildUp(self):
        if not self.done:
            self.addButtons()
            self.done = True

#Card class inherits Image for showing back and face of the card
#and ButtonBehavior for acting like a button and being presed.
#Card has its own position on a play feild, so that application
#knows which card was presed.
class Card(ButtonBehavior, Image):

    coords = ListProperty([0, 0])
    card_pos_x = 0
    card_pos_y = 0

    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)

        self.source = os.path.join(dir_path,'Source', 'Card-Back-01.png')

        self.allow_stretch = True
        self.keep_ratio = True
        self.flipped = False
        self.card_rank=None
        self.card_suit=None

#Setting card suit and rank.
    def set_card_rand(self, card_rank,card_suit):
        self.card_rank = card_rank
        self.card_suit = card_suit

    def get_card_suit(self):
       return self.card_suit

    def get_card_rank(self):
        return self.card_rank

#Setting image for the face of the card according to its rank and suit
    def set_source_face(self,face):
        self.face=resource_find(os.path.join(dir_path,'Source','Classic', face))
        print self.face
        return self.face

    def set_source_back(self):
        self.back=os.path.join(dir_path, 'Source', 'Card-Back-01.png')
        return self.back

#Flipping the card- changing its back with face and reverse.
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

#Check if card flipped or not.
    def get_flipped_state(self):
        return self.flipped

#CardDesk class inherits GridLayout for better and controled
#plecament of objects on the play feild.
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
        self.height = Window.height*9/10
        self.x = Window.width - self.width
        self.y = Window.height*9/10 - self.height
        self.cardList = None
        self.spacing = [50, 20]

#Setting sizes of the feild in rows and columns.
    def set_bounds(self, ip_rows, ip_cols):
        self.rows = ip_rows
        self.cols = ip_cols
        self.cardList = None
        self.cardList = range(ip_rows * ip_cols)
        print 'Card list:%s' % self.cardList

#Randomizing card's rank and suit.
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

#Main game process with compearing of pressed pair of cards.
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

#Adding cards on the feild.
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
                # source=str(self.card_stack[row *self.cols+column].get_card_suit())+\
                #        str((self.card_stack[row *self.cols+column].get_card_rank()))+'.png'
                source = str(self.card_stack[row * self.cols + column].get_card_suit()) + \
                         str((self.card_stack[row * self.cols + column].get_card_rank())) + '.png'
                print 'Card suit:%s rank:%s' % (
                self.card_stack[row *self.cols+column].get_card_suit(), self.card_stack[row *self.cols+column].get_card_rank())
                print 'Source: %s' % source
                self.card_stack[row * self.cols + column].set_source_face(str(source))

    def buildUp(self):
        self.addCards()

#Remowing cards for the field.
    def remove(self):
        for row in range(self.rows):
            for column in range(self.cols):
                    self.remove_widget(self.card_stack[row *self.cols+column])

#Flipping chosen card.
    def flip_card(self,fl_row,fl_col):
        self.card_stack[fl_row*self.cols+fl_col].flip()
        print 'I flipped!! r:%s c:%s' %(fl_row,fl_col)

#Checking if game over or not.
    def check_flipped_cards(self):
        for row in range(self.rows):
            for column in range(self.cols):
                if not self.card_stack[row *self.cols+column].get_flipped_state():
                    return 0
        return 1

#ClientApp is main application part it is app itself.
class ClientApp(App):
    def build(self):

        self.parent = Widget()

        self.sm = StartMenu()
        self.sm.buildUp()

        self.bm=BoardMenu()

        self.lm = LevelMenu()
        self.cl=CustomLevel()

#Checking which button was pressed and acting accordinly on customlevel menu.

        def check_custlevel_button(obj):

            if self.cl.buttonText == 'Ok':

                self.de = CardDesk()
                self.de.set_bounds(self.cl.custom_row,self.cl.custom_column)
                self.de.buildUp()
                self.parent.remove_widget(self.cl)

                self.bm.buildUp()
                self.parent.add_widget(self.bm)

                self.parent.add_widget(self.de)
                print ' we should start the game now custom'

            if self.cl.buttonText == 'Cancel':
                self.parent.remove_widget(self.cl)
                self.parent.add_widget(self.sm)
                print 'Cancel'

# Checking which button was pressed and acting accordinly on level menu.
        def check_level_button(obj):

            if self.lm.buttonText == 'Easy':
                self.parent.remove_widget(self.lm)
                self.de = CardDesk()
                self.de.set_bounds(3, 4)

                self.bm.buildUp()
                self.parent.add_widget(self.bm)

                self.de.buildUp()
                self.parent.add_widget(self.de)
                print ' we should start the game now easy'

            if self.lm.buttonText == 'Medium':
                self.parent.remove_widget(self.lm)
                self.de = CardDesk()
                self.de.set_bounds(4, 5)

                self.bm.buildUp()
                self.parent.add_widget(self.bm)

                self.de.buildUp()
                self.parent.add_widget(self.de)
                print ' we should start the game now medium'

            if self.lm.buttonText == 'Hard':
                self.parent.remove_widget(self.lm)
                self.de = CardDesk()
                self.de.set_bounds(5, 6)

                self.bm.buildUp()
                self.parent.add_widget(self.bm)

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

# Checking which button was pressed and acting accordinly on board menu.
        def check_board_button(obj):
            # check to see which button was pressed

            if self.bm.buttonText == 'Exit':
                self.parent.remove_widget(self.bm)
                self.parent.remove_widget(self.de)
                self.parent.add_widget(self.sm)
                print ' Exit'

# Checking which button was pressed and acting accordinly on start menu.
        def check_start_button(obj):
            # check to see which button was pressed
            if self.sm.buttonText == 'Start':
                self.parent.remove_widget(self.sm)
                self.parent.add_widget(self.lm)
                self.lm.buildUp()

            if self.sm.buttonText == 'Settings':
                self.parent.remove_widget(self.sm)
                print ' Score table'

            if self.sm.buttonText == 'Exit':
                self.parent.remove_widget(self.parent)
                App.get_running_app().stop()
                print ' Exit'

#Event sending:
        self.sm.bind(on_button_release=check_start_button)
        self.lm.bind(on_button_release=check_level_button)
        self.cl.bind(on_button_release=check_custlevel_button)
        self.bm.bind(on_button_release=check_board_button)

        self.parent.add_widget(self.sm)

        return self.parent

if __name__ == '__main__':
    ClientApp().run()
