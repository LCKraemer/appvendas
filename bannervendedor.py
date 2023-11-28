from botoes import ImageButton, LabelButton
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.app import App
from functools import partial
import requests

class BannerVendedor(FloatLayout):
    def __init__(self, **kwargs):  # init reescreve info da super(GridLayout). Classe perde caracteristicas da super.
        super().__init__()  # chamar o init da super dentro do init da classe adiciona o conteudo no init da classe

        self.rows = 1

        with self.canvas:
            Color(rgb=(0, 0, 0, 1))
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualizar_rec, size=self.atualizar_rec)

        my_app = App.get_running_app()

        id_vendedor = kwargs["id_vendedor"]
        link = f'https://aplicativovendasdb-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"'
        request = requests.get(link)
        request_dic = request.json()
        valor = list(request_dic.values())[0]
        avatar = valor["avatar"]
        total_vendas = valor["total_vendas"]

        imagem = ImageButton(source=f"icones/fotos_perfil/{avatar}",
                             pos_hint={"right": 0.4, "top": 0.9}, size_hint=(0.3, 0.8),
                             on_release=partial(my_app.carregar_vendas_vendedor, valor))
        label_id = LabelButton(text=f"ID: {id_vendedor}",
                               pos_hint={"right": 0.9, "top": 0.9}, size_hint=(0.5, 0.5),
                               on_release=partial(my_app.carregar_vendas_vendedor, valor))
        label_total_vendas = LabelButton(text=f"Total de vendas R${total_vendas}",
                                         pos_hint={"right": 0.9, "top": 0.6}, size_hint=(0.5, 0.5),
                                         on_release=partial(my_app.carregar_vendas_vendedor, valor))
        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total_vendas)


    def atualizar_rec(self, *args):
        self.rec.pos = self.pos
        self.rec.size = self.size
