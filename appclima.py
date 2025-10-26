from flask import Flask, render_template, request  # Importa Flask e funções para criar site, pegar dados do usuário e renderizar HTML
import requests  # Importa para fazer requisições HTTP para APIs externas

app = Flask(__name__)  # Cria a aplicação Flask, base do seu site

# Chaves da API - você pega na sua conta OpenWeather
chave_api_local = "0a09ad0d76888335e36a286cd4cf5350"  # Geocoding reverso (lat/lon para cidade/estado)
chave_api_clima = "4e31f5a59f6c33de31132091edb51601"  # API do OpenWeather para clima
url_clima = "https://api.openweathermap.org/data/2.5/weather"  # URL da API de clima

# Função que, dado o nome da cidade, retorna o estado (ex: "São Paulo")
def obter_estado_por_cidade(cidade):
    url = "http://api.openweathermap.org/geo/1.0/direct"  # Endpoint de geocoding direto (cidade → lat/lon/estado)
    params = {
        "q": cidade,  # Cidade que queremos buscar
        "limit": 1,   # Queremos só 1 resultado (o mais relevante)
        "appid": chave_api_local,  # Autenticação da API
        "lang": "pt-br"
    }
    resposta = requests.get(url, params=params)  # Faz a requisição GET para API
    if resposta.status_code == 200:  # Se deu certo (200 é sucesso)
        dados = resposta.json()  # Converte a resposta JSON para dicionário Python
        if dados:  # Se tem dados na lista
            return dados[0].get("state")  # Retorna o campo "state" do primeiro resultado
    return None  # Se não achar, retorna None


# Função que, dado lat e lon, retorna a localização (cidade, estado, etc) usando geocoding reverso
def obter_localizacao(lat, lon):
    url_localization = "http://api.openweathermap.org/geo/1.0/reverse"  # Endpoint para geocoding reverso
    params = {
        "lat": lat,
        "lon": lon,
        "appid": chave_api_local,
        "lang": "pt-br"
    }
    resposta = requests.get(url_localization, params=params, timeout=5)  # Faz requisição GET com timeout de 5 segundos
    if resposta.status_code == 200:
        data = resposta.json()
        if data:
            return data  # Retorna lista de locais próximos
    return None


# Função que busca dados do clima, pode ser por cidade ou lat/lon
def obter_clima(cidade=None, lat=None, lon=None):
    params = {
        "appid": chave_api_clima,
        "units": "metric",  # Temperatura em °C
        "lang": "pt_br"     # Resposta em português brasileiro
    }
    if lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    elif cidade:
        params["q"] = cidade
    else:
        params["q"] = "São Paulo"  # Se nada passar, usa São Paulo como padrão

    try:
        resposta = requests.get(url_clima, params=params, timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
    except requests.RequestException:
        pass  # Se der erro, ignora e retorna None

    return None


# Rota principal do site ("/") aceita GET e POST
@app.route("/", methods=["GET", "POST"])
def index():
    clima = None  # Aqui vamos guardar os dados do clima que vamos mostrar
    erro = None   # Caso dê erro, mensagem será guardada aqui

    if request.method == "POST":
        # Pega a cidade do formulário HTML que o usuário digitou
        cidade = request.form.get("cidade", "").strip()
        print("POST recebido, cidade:", cidade)
        if cidade:
            dados = obter_clima(cidade=cidade)  # Busca o clima pelo nome da cidade
            print("Dados do clima pelo nome da cidade:", dados)
            if dados:
                clima = extrair_dados_clima(dados)  # Extrai só os dados importantes para mostrar
                estado = obter_estado_por_cidade(cidade)  # Busca o estado via geocoding direto
                clima["estado"] = estado  # Adiciona estado no dicionário clima
            else:
                erro = "Cidade não encontrada ou erro na API."
        else:
            erro = "Digite uma cidade válida."
    else:
        # Se for GET, tenta pegar latitude e longitude na URL (exemplo: ?lat=-23.5&lon=-46.6)
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        print("GET recebido, lat:", lat, "lon:", lon)

        if lat and lon:
            dados = obter_clima(lat=lat, lon=lon)  # Busca clima por coordenadas
            print("Dados do clima por lat/lon:", dados)
            if dados:
                clima = extrair_dados_clima(dados)
                localizacao = obter_localizacao(lat, lon)  # Geocoding reverso para pegar estado
                print("Localizacao obtida pelo geocoding reverso:", localizacao)
                if localizacao and len(localizacao) > 0:
                    clima["estado"] = localizacao[0].get("state")  # Adiciona estado
                else:
                    clima["estado"] = None
            else:
                # Se não conseguir o clima, tenta só obter localização
                localizacao = obter_localizacao(lat, lon)
                print("Localizacao obtida (tentativa fallback):", localizacao)
                if localizacao and len(localizacao) > 0:
                    cidade = localizacao[0].get("name")
                    clima["estado"] = localizacao[0].get("state")
                    print("Cidade extraída:", cidade)
                    if cidade:
                        dados = obter_clima(cidade=cidade)
                        print("Dados do clima após obter cidade do geocoding:", dados)
                        if dados:
                            clima = extrair_dados_clima(dados)
                            clima["estado"] = None
                        else:
                            erro = "Não foi possível obter clima para a cidade encontrada."
                    else:
                        erro = "Não foi possível determinar a cidade para as coordenadas."
                else:
                    erro = "Não foi possível obter a localização."
        else:
            # Se não passou nada, busca clima padrão de São Paulo
            dados = obter_clima()
            print("Dados do clima padrão (São Paulo):", dados)
            if dados:
                clima = extrair_dados_clima(dados)

    print("Final clima:", clima)
    print("Final erro:", erro)

    # Envia para o template HTML para renderizar e mostrar na página
    return render_template("index.html", clima=clima, erro=erro)


# Função que pega só os dados importantes do JSON da API para facilitar uso no template
def extrair_dados_clima(dados):
    return {
        "nome": dados.get("name"),
        "estado": dados.get("state"),
        "pais": dados["sys"].get("country"),
        "descricao": dados["weather"][0].get("description", "").capitalize(),
        "temp": dados["main"].get("temp"),
        "sensacao": dados["main"].get("feels_like"),
        "umidade": dados["main"].get("humidity"),
        "vento": dados["wind"].get("speed")
    }


# Se rodar esse arquivo diretamente, inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)  # Debug = True para mostrar erros e reiniciar automaticamente
