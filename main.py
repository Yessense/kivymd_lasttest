import os
import sys
import threading

import requests
import asyncio
import urllib, json
from urllib.request import urlopen

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.uix.list import OneLineAvatarListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivy.loader import Loader


if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["MYAPP_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["MYAPP_ROOT"] = os.path.dirname(os.path.abspath(__file__))
    os.environ["MYAPP_ASSETS"] = os.path.join(
        os.environ["MYAPP_ROOT"], f"assets{os.sep}")
    os.environ["KIVY_IMAGE"] = "pil"

class RecView(RecycleView):
    def __init__(self, **kwargs):
        self.values = kwargs.pop('values')
        self.pictures = kwargs.pop('pictures')
        super(RecView, self).__init__(**kwargs)
        print(self.pictures)
        self.data = [{'text': self.values[x], 'source': self.pictures[x]} for x in range(len(self.values))]

class SplashScreen(Screen):
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
            url_image_path = os.path.join(self.url_image, self.data[i]['graphic'])
            file_image_path = os.path.join(os.environ["MYAPP_ROOT"], "temp", self.data[i]['graphic'])
            if not os.path.isfile(file_image_path):
                try:
                    urllib.request.urlretrieve(url_image_path, file_image_path)
                    self.pictures.append(os.path.join("./temp", self.data[i]['graphic']))
                except:
                    self.pictures.append("./assets/No-image-available.png")

            self.text.append(self.data[i]['name'])
            print(i)
        print("done")
        # app = MDApp.get_running_app()
        # app.root.screen

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
        pass
        # self.root.current = 'RecycleScreen'





ViewPagerApp().run()