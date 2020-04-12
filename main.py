import os
import sys
import threading
import certifi



import urllib, json
from urllib.request import urlopen

from kivy.clock import Clock, mainthread
from kivy.core.text import Label
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.uix.button import Button
from kivymd.uix.list import  OneLineAvatarListItem
from kivymd.uix.tab import MDTabsBase


if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["MYAPP_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["MYAPP_ROOT"] = os.path.dirname(os.path.abspath(__file__))
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ["MYAPP_ASSETS"] = os.path.join(
        os.environ["MYAPP_ROOT"], f"assets{os.sep}")
    os.environ["KIVY_IMAGE"] = "pil"

class MyRecycleBoxLayout(RecycleBoxLayout,FocusBehavior, LayoutSelectionBehavior):
    pass

class RecView(RecycleView):
    def __init__(self, **kwargs):
        self.values = kwargs.pop('values',None)
        self.pictures = kwargs.pop('pictures',None)
        super(RecView, self).__init__(**kwargs)
        self.data = [{'text': self.values[x], 'source': self.pictures[x] } for x in range(len(self.values))]

class MyOneLineAvatarListItem(OneLineAvatarListItem,RecycleDataViewBehavior):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(MyOneLineAvatarListItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(MyOneLineAvatarListItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            print(rv.data[index]['text'])
            app = MDApp.get_running_app()
            app.root.current = "TabScreen"

class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''

class SplashScreen(Screen):
    stop = threading.Event()
    def __init__(self,**kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.data = []

        self.pictures = []
        self.text = []
        self.url_data = "https://raw.githubusercontent.com/" \
                        "wesleywerner/ancient-tech/" \
                        "02decf875616dd9692b31658d92e64a20d99f816/" \
                        "src/data/techs.ruleset.json"
        self.url_image = "https://raw.githubusercontent.com/" \
                    "wesleywerner/ancient-tech/" \
                    "02decf875616dd9692b31658d92e64a20d99f816/" \
                    "src/images/tech/"
        self.app = MDApp.get_running_app()

    def load(self):
        print("load started")
        x = threading.Thread(target=self.load_data_json)

        x.start()

        print("load ended")
    def load_data_json(self):
        Clock.schedule_once(self.start_anim, 0)
        json_url = urlopen(self.url_data)
        self.data = json.loads(json_url.read())
        print(self.data)
        for i in range(1, len(self.data)):
            if self.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return
            url_image_path = os.path.join(self.url_image, self.data[i]['graphic'])
            file_image_path = os.path.join(os.environ["MYAPP_ROOT"], "temp", self.data[i]['graphic'])
            self.pictures.append("./assets/No-image-available.png")
            # if os.path.isfile(file_image_path):
            #     self.pictures.append(os.path.join("./temp", self.data[i]['graphic']))
            # else:
            #     try:
            #         urllib.request.urlretrieve(url_image_path, file_image_path)
            #
            #     except:
            #         self.pictures.append("./assets/No-image-available.png")
            self.text.append(self.data[i]['name'])
            print(i)

        # self.app.pictures = self.pictures
        # self.app.text = self.text
        print("done")
        view = RecView(values=self.text,pictures=self.pictures)
        self.parent.ids.recview.add_widget(view)
        self.parent.current = 'RecycleScreen'
        self.get_tabs_ready()



    def get_tabs_ready(self):
        print(len(self.pictures))
        print(len(self.text))
        for i in range(len(self.text)):
            tab = Tab(text=self.text[i])
            tab.ids.anchor.add_widget(Image(source=self.pictures[i]))
            self.app.root.ids.tabs.add_widget(tab)


    def start_anim(self, *args):
        print("anim looped")
        anim_bar = Factory.AnimWidget()
        self.anim_box.add_widget(anim_bar)

        # Animate the added widget.
        anim = Animation(opacity=0.3, width=100, duration=0.6)
        anim += Animation(opacity=1, width=400, duration=0.8)
        anim.repeat = True
        anim.start(anim_bar)


class ViewPagerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Teal"

        self.data = []
        self.pictures = []

    def build(self):
        Builder.load_file(f"{os.environ['MYAPP_ROOT']}/kv/RecView.kv")
        Builder.load_file(f"{os.environ['MYAPP_ROOT']}/kv/SplashScreen.kv")
        return Builder.load_file(f"{os.environ['MYAPP_ROOT']}/kv/ViewPager.kv")

    def on_start(self):
        self.root.ids.splashscreen.load()

    def on_tab_switch(
                self, instance_tabs, instance_tab, instance_tab_label, tab_text
        ):
        instance_tab.ids.label.text = tab_text


    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.ids.splashscreen.stop.set()


ViewPagerApp().run()