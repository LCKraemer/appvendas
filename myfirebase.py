import requests
from kivy.app import App

class MyFirebase():
    API_KEY = "AIzaSyCc1gyrexmxbDOLOvm_h_544mL-1ga3eDs"

    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"

        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        request = requests.post(link, data=info)
        req_dic = request.json()
        #print(req_dic)
        my_app = App.get_running_app()
        login_page = my_app.root.ids["loginpage"]

        if request.ok:
            # req_dic["idToken"] -> autenticação
            # req_dic["refreshToken"] -> token que mantem o user logado
            # req_dic["localId"] -> id do usuario

            refresh_token = req_dic["refreshToken"]
            id_token = req_dic["idToken"]
            local_id = req_dic["localId"]

            my_app.local_id = local_id
            my_app.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            request_id = requests.get(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/proximo_id.json"
                                      f"?auth={id_token}")
            id_vendedor = request_id.json()
            link = f"https://aplicativovendasdb-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "", "id_vendedor": "{id_vendedor}"}}'
            user_request = requests.patch(link, data=info_usuario)

            prox_id = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id": "{prox_id}"}}'
            requests.patch(f"https://aplicativovendasdb-default-rtdb.firebaseio.com/.json?auth={id_token}",
                           data=info_id_vendedor)


            mensagem_sucesso = "Usuário Criado"
            login_page.ids["mensagem_login"].text = mensagem_sucesso
            login_page.ids["mensagem_login"].color = (0, 0.4859, 0.5141, 1)

            my_app.carregar_info_usuario()
            my_app.mudar_tela("homepage")
        else:
            mensagem_erro = req_dic["error"]["message"]
            if mensagem_erro == "MISSING_PASSWORD":
                mensagem_erro = "SENHA FALTANDO"
            elif mensagem_erro == "INVALID_EMAIL":
                mensagem_erro = "E-MAIL INVÁLIDO"
            elif "WEAK_PASSWORD" in mensagem_erro:
                mensagem_erro = "SENHA MUITO FRACA"
            elif mensagem_erro == "MISSING_PASSWORD":
                mensagem_erro = "SENHA FALTANDO"
            elif mensagem_erro == "MISSING_PASSWORD":
                mensagem_erro = "SENHA FALTANDO"

            login_page.ids["mensagem_login"].text = mensagem_erro
            login_page.ids["mensagem_login"].color = (1, 0, 0, 1)
    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        request = requests.post(link, data=info)
        req_dic = request.json()
        my_app = App.get_running_app()
        login_page = my_app.root.ids["loginpage"]

        if request.ok:
            # req_dic["idToken"] -> autenticação
            # req_dic["refreshToken"] -> token que mantem o user logado
            # req_dic["localId"] -> id do usuario
            mensagem_sucesso = "Login realizado"
            login_page.ids["mensagem_login"].text = mensagem_sucesso
            login_page.ids["mensagem_login"].color = (0, 0.4859, 0.5141, 1)

            refresh_token = req_dic["refreshToken"]
            id_token = req_dic["idToken"]
            local_id = req_dic["localId"]

            my_app.local_id = local_id
            my_app.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)


            my_app.carregar_info_usuario()
            my_app.mudar_tela("homepage")
        else:
            mensagem_erro = req_dic["error"]["message"]
            if mensagem_erro == "MISSING_PASSWORD":
                mensagem_erro = "SENHA FALTANDO"
            elif mensagem_erro == "INVALID_EMAIL":
                mensagem_erro = "E-MAIL INVÁLIDO"
            elif "WEAK_PASSWORD" in mensagem_erro:
                mensagem_erro = "SENHA MUITO FRACA"
            elif mensagem_erro == "INVALID_LOGIN_CREDENTIALS":
                mensagem_erro = "CREDENCIAIS DE LOGIN INVÁLIDAS"
            elif mensagem_erro == "MISSING_PASSWORD":
                mensagem_erro = "SENHA FALTANDO"

            login_page.ids["mensagem_login"].text = mensagem_erro
            login_page.ids["mensagem_login"].color = (1, 0, 0, 1)
    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        request = requests.post(link, data=info)
        req_dic = request.json()
        local_id = req_dic["user_id"]
        id_token = req_dic["id_token"]
        return local_id, id_token