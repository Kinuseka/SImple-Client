import kivy
from kivy.app import App 
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.textinput import TextInput 
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.clock import Clock
from kivy.core.window import Window
from threading import Thread
import Lib
import Loader
import sys
import io
import asyncio

sm = ScreenManager()
pages = None
current = None

class ThreadReturn(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def Https_checker(data):
  """For MODDERS:
  1.If you want to add a Link verifier to prevent invalid link error then you have nothing to edit here, however you can delete this to disable this feature.
  2.You can modify the 1st condition if the target site does not support or does not use numbers to identify their gallery.
  3.If you want to use links, be sure that the user has to include http:// or https:// to prevent further problems.
  """
  if data.isdigit():
    data = Lib.CheckLink(data, opt=True)
    return(0,data)
  elif "http://" in data or "https://" in data:
    result,data = Lib.CheckLink(data)
    return(result,data)
  else:
    return(1,"A link should have http:// or https://")

class Scroll(ScrollView):
    hill = ObjectProperty(None)
    def __init__(self,**args):
        super().__init__(**args)
        #thread1 = Thread(target=Loader.LoadImage,args=(self,pages))
        #thread1.start()
        global event
        self.pages = pages
        Window.bind(on_keyboard=self.Android_back)
        event = Clock.create_trigger(self.LoadImage)
    
    
    def LoadImage(self,*a):
        images = []
        self.searched = current          
        thread1 = Thread(target=self.AsyncStart, args=(self,pages,))
        thread1.start()
    
    def AsyncStart(self,*args):   
        asyncio.run(Loader.threadhandler(*args))
            
    def Android_back(self,window,key,*kwargs):
        if key == 27:
            sm.current = 'home'
            sm.remove_widget(Scroll(name='scroll'))
        

class Box(StackLayout):
    pages = pages
    

class Pages(Screen):
    pass
    
        
        

class home(Screen):
    code = ObjectProperty(None)
    status = ObjectProperty(None)
    status2 = ObjectProperty(None)
    sutton = ObjectProperty(None)
    viewsutton = ObjectProperty(None)
    
    def __init__(self,**args):
         super().__init__(**args)  
         self.searched = False  
         

    def Update_button(self):
        if self.searched:
            self.viewsutton.disabled = False     
        else:
            self.viewsutton.disabled = True        
    
    def Switch(self):
        global pages
        global current
        current = self.searched
        pages = self.searched.Pages()
        print(pages)
        sm.add_widget(Pages(name='show'))
        sm.current = "show"
        event()
        
    
    def Result(self):
        link = Https_checker(self.code.text)
        print(self.code.text)
        Loader.setLabel(self.status, "Searching...")
        Loader.setLabel(self.code, "")
        if link[0] == 0:
            usr_input = link[1]
        else:
            Loader.setLabel(self.status, "Enter a valid link or value")
            return
        thread1 = Thread(target=Loader.Search,args=(self,usr_input,))
        thread1.start()
        
class myFormat(FloatLayout):
    code = ObjectProperty(None)
    def button(self):
        print(self.code.text)
        self.code.text = ""
    
class myApp(App):
    def build(self):
        sm.add_widget(home(name="home"))
        return sm
  
  
if __name__ == "__main__":
    myApp().run()
