from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
from myfirebase import MyFirebase
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
import requests
from kivy.core.window import Window
import os
import certifi
from datetime import date
from functools import partial  # permite que um parametro seja passado para uma função usada como parametro

os.environ["SSL_CERT_FILE"] = certifi.where()

GUI = Builder.load_file("main.kv")
class MainApp(App):
    #Window.size = (360, 640)  # changing window size to match 16:9 phone resolution. might have to delete later.

    cliente = None
    produto = None
    unidade = None
    def on_start(self):
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        self.carregar_info_usuario()
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto}",
                                 on_release=partial(self.selecionar_cliente, foto))
            label = LabelButton(text=foto.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_cliente, foto))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        # -----------------
        arquivos = os.listdir("icones/fotos_produtos")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto}",
                on_release=partial(self.selecionar_produto, foto))
            label = LabelButton(text=foto.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_produto, foto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)


        label_data = pagina_adicionarvendas.ids["label_data"]
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"
    def build(self):
        self.firebase = MyFirebase()
        return GUI


    def carregar_info_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
            requisicao = requests.get(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{self.local_id}.json"
                                      f"?auth={self.id_token}")
            requisicao_dic = requisicao.json()

            # foto
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            # id
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_vendedor"].text = f"ID {id_vendedor}"

            # equipe
            self.equipe = requisicao_dic['equipe']

            # total de vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vandas = total_vendas
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#000000]Total de vendas:[/color] [b]R${total_vendas}[/b]"



            # lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids["homepage"]
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]

                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                         produto=venda["produto"], foto_produto=venda["foto_produto"],
                                         data=venda["data"], unidade=venda["unidade"],
                                         preco=venda["preco"], quantidade=venda["quantidade"])

                    lista_vendas.add_widget(banner)

            except:
                pass
            equipe = requisicao_dic["equipe"]
            lista_equipe = equipe.split(",")
            pagina_listavendedores = self.root.ids["listarvendedorespage"]
            lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)
            self.mudar_tela("homepage")
        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela
    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        info = f'{{"avatar": "{foto}"}}'  # a chave e o valor devem estar em aspas duplas. como o valor não é uma
        # string, precisamos também usar uma fstring. mas as chaves exteriores se confundem o codigo.
        # a solução é usar DUAS chaves. Ou seja, sempre copiar este molde para alterar no banco do firebase.
        requisicao = requests.patch(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{self.local_id}.json"
                                    f"?auth={self.id_token}",
                                    data=info)

        self.avatar = foto
        
    def adicionar_vendedor(self, id_vendedor):
        link = f'https://aplicativovendasdb-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="' \
               f'{id_vendedor}"'
        request = requests.get(link)
        req_dic = request.json()

        pagina_adicionarvendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adicionarvendedor.ids["mensagem_outrovendedor"]

        if req_dic == {}:
            mensagem_texto.text = "Usuário não encontrado."
        else:
            equipe = self.equipe.split(",")
            if id_vendedor in equipe:
                mensagem_texto.text = "Vendedor já faz parte da equipe."
            else:
                self.equipe = self.equipe + f",{id_vendedor}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{self.local_id}.json"
                               f"?auth={self.id_token}",
                               data=info)
                mensagem_texto.text = "Vendedor adicionado com sucesso."
                # adicionando o novo banner
                pagina_listavendedores = self.root.ids["listarvendedorespage"]
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):


        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 1, 1, 1)
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        self.cliente = foto.replace(".png", "")
        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]

        pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 1, 1, 1)
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        self.produto = foto.replace(".png", "")
        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id, *args):
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        self.unidade = id.replace("unidades_", "")
        pagina_adicionarvendas.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)

        pagina_adicionarvendas.ids[id].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids["preco_total"].text
        quantidade = pagina_adicionarvendas.ids["quantidade_total"].text

        if not cliente:
            print("not cliente")
            pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 0, 0, 1)
        if not produto:

            print("not produto")
            pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 0, 0, 1)
        if not unidade:

            print("not unidade")
            pagina_adicionarvendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_litros"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 0, 0, 1)

        if not preco:

            print("not preco")
            pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)

        if not quantidade:

            print("not quantidade")
            pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)

        if cliente and produto and unidade and preco and quantidade:
            if (type(preco) == float) and (type(quantidade) == float):
                foto_produto = produto + ".png"
                foto_cliente = cliente + ".png"
                print(foto_cliente)
                info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", ' \
                       f'"foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", ' \
                       f'"preco": "{preco}", "quantidade": "{quantidade}"}}'
                requests.post(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{self.local_id}/vendas.json"
                              f"?auth={self.id_token}",
                              data=info)


                banner = BannerVenda(cliente=cliente, produto=produto, quantidade=quantidade, data=data, preco=preco,
                                     foto_cliente=foto_cliente, foto_produto=foto_produto, unidade=unidade)

                pagina_homepage = self.root.ids["homepage"]
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                lista_vendas.add_widget(banner)

                request = requests.get(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{self.local_id}/"
                                       f"total_vendas.json?auth={self.id_token}")
                total_vendas = float(request.json())
                total_vendas += preco
                info = f'{{"total_vendas": "{total_vendas}"}}'
                requests.patch(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{self.local_id}.json"
                               f"?auth={self.id_token}",
                               data=info)
                homepage = self.root.ids["homepage"]
                homepage.ids["label_total_vendas"].text = f"[color=#000000]Total de vendas:[/color] " \
                                                          f"[b]R${total_vendas}[/b]"
                self.mudar_tela("homepage")

        self.cliente = None
        self.produto = None
        self.unidade = None

        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
            except:
                pass
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
            except:
                pass

    def carregar_todas_vendas(self):

        pagina_todasvendas = self.root.ids["todasvendaspage"]
        lista_vendas = pagina_todasvendas.ids["lista_vendas"]

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        requisicao = requests.get(f'https://aplicativovendasdb-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()

        # foto
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/hash.png"

        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda["preco"])
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                         produto=venda["produto"], foto_produto=venda["foto_produto"],
                                         data=venda["data"], unidade=venda["unidade"],
                                         preco=venda["preco"], quantidade=venda["quantidade"])
                    lista_vendas.add_widget(banner)
            except:
                pass

        # total de vendas
        pagina_todasvendas.ids["label_total_vendas"].text = f"[color=#000000]Total de vendas:[/color] [b]R$" \
                                                            f"{total_vendas}[/b]"





        self.mudar_tela("todasvendaspage")

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"
        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_vendedor, *args):

        total_vendas = dic_vendedor["total_vendas"]
        try:
            vendas = dic_vendedor["vendas"]
            pagina_vendasoutrovendedor = self.root.ids["vendasoutrovendedorpage"]
            lista_vendas = pagina_vendasoutrovendedor.ids["lista_vendas"]
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                     produto=venda["produto"], foto_produto=venda["foto_produto"],
                                     data=venda["data"], unidade=venda["unidade"],
                                     preco=venda["preco"], quantidade=venda["quantidade"])
                lista_vendas.add_widget(banner)
        except:
            pass

        pagina_vendasoutrovendedor.ids["label_total_vendas"].text = f"[color=#000000]Total de vendas:[/color] [b]R$" \
                                                                    f"{total_vendas}[/b]"

        foto_perfil = self.root.ids["foto_perfil"]
        avatar = dic_vendedor["avatar"]
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"
        self.mudar_tela("vendasoutrovendedorpage")

MainApp().run()

