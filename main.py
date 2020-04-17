import json
import os
import sys
import threading
import certifi

from urllib.request import urlopen

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarListItem, ILeftBody
from kivymd.uix.tab import MDTabsBase, MDTabs

if getattr(sys, "frozen", False):
    os.environ["MYAPP_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["MYAPP_ROOT"] = os.path.dirname(os.path.abspath(__file__))
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ["MYAPP_ASSETS"] = os.path.join(
        os.environ["MYAPP_ROOT"], f"assets{os.sep}")
    os.environ["KIVY_IMAGE"] = "pil"


class MyImageLeft(ILeftBody, AsyncImage):
    pass


class MyRecycleBoxLayout(RecycleBoxLayout, FocusBehavior, LayoutSelectionBehavior):
    pass


class RecView(RecycleView):
    def __init__(self, **kwargs):
        self.values = kwargs.pop('values', None)
        self.pictures = kwargs.pop('pictures', None)
        super(RecView, self).__init__(**kwargs)
        self.data = [{'text': self.values[x], 'path': self.pictures[x]} for x in range(len(self.values))]


class MyOneLineAvatarListItem(OneLineAvatarListItem, RecycleDataViewBehavior):
    """ Add selection support to the Label """
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
        """ Respond to the selection of items in the view. """
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            print(rv.data[index]['text'])
            app = MDApp.get_running_app()
            app.show_tab_screen(index)


class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''
    pass


class SplashScreen(Screen):

    def __init__(self, **kwargs):
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
        self.text = []
        self.decription = []

        self.url_data = "https://raw.githubusercontent.com/" \
                        "wesleywerner/ancient-tech/" \
                        "02decf875616dd9692b31658d92e64a20d99f816/" \
                        "src/data/techs.ruleset.json"
        self.url_image = "https://raw.githubusercontent.com/" \
                         "wesleywerner/ancient-tech/" \
                         "02decf875616dd9692b31658d92e64a20d99f816/" \
                         "src/images/tech/"

    def build(self):
        Builder.load_file(f"{os.environ['MYAPP_ROOT']}/kv/RecView.kv")
        Builder.load_file(f"{os.environ['MYAPP_ROOT']}/kv/SplashScreen.kv")
        return Builder.load_file(f"{os.environ['MYAPP_ROOT']}/kv/ViewPager.kv")

    def on_start(self):
        self.load()

    def load_data_json(self):
        Clock.schedule_once(self.root.ids.splashscreen.start_anim, 0)
        json_url = urlopen(self.url_data)
        self.data = json.loads(json_url.read())
        print(self.data)
        for i in range(1, len(self.data)):
            desc = ''
            desc += "Требование 1: " + self.data[i].get('req1', "Нет") + "\n"
            desc += "Требование 2: " + self.data[i].get('req2', "Нет") + "\n"
            desc += "Подсказка: " + self.data[i].get('helptext', '')
            self.decription.append(desc)
            self.text.append(self.data[i]['name'])
            url_image_path = os.path.join(self.url_image, self.data[i]['graphic'])
            self.pictures.append(url_image_path)
        self.create_recycle_view()

    def create_recycle_view(self):
        view = RecView(values=self.text, pictures=self.pictures)
        self.root.ids.recview.add_widget(view)
        self.root.current = 'RecycleScreen'

    def show_tab_screen(self, index):
        tabs = MDTabs()
        tabs.default_tab = index
        for i in range(len(self.text)):
            tab = Tab(text=self.text[i])
            tab.desc = "\n" + self.decription[i]
            tab.ids.anchor.add_widget(AsyncImage(source=self.pictures[i]))
            tabs.add_widget(tab)

        self.root.ids.boxtabs.add_widget(tabs)
        self.root.current = "TabScreen"

    def load(self):
        print("load started")
        threading.Thread(target=self.load_data_json).start()


ViewPagerApp().run()
