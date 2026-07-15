from flask import Flask, render_template, request  # Importa Flask e funções para criar site, pegar dados do usuário e renderizar HTML
import requests  # Importa para fazer requisições HTTP para APIs externas

app = Flask(__name__)  # Cria a aplicação Flask, base do seu site

# Chaves da API - você pega na sua conta OpenWeather
chave_api_local = "0a09ad0d76888335e36a286cd4cf5350"  # Geocoding reverso (lat/lon para cidade/estado)
chave_api_clima = "4e31f5a59f6c33de31132091edb51601"  # API do OpenWeather para clima
url_clima = "https://api.openweathermap.org/data/2.5/weather"  # URL da API de clima


# Dicionário de tradução de siglas de países (Padrão ISO 3166-1 Alpha-2)
paises_siglas = {
    "AF": "Afeganistão", "ZA": "África do Sul", "AL": "Albânia", "DE": "Alemanha", "AD": "Andorra",
    "AO": "Angola", "AI": "Anguilla", "AQ": "Antártida", "AG": "Antígua e Barbuda", "SA": "Arábia Saudita",
    "DZ": "Argélia", "AR": "Argentina", "AM": "Armênia", "AW": "Aruba", "AU": "Austrália",
    "AT": "Áustria", "AZ": "Azerbaijão", "BS": "Bahamas", "BD": "Bangladesh", "BB": "Barbados",
    "BH": "Bahrein", "BE": "Bélgica", "BZ": "Belize", "BJ": "Benim", "BM": "Bermudas",
    "BY": "Bielorrússia", "BO": "Bolívia", "BA": "Bósnia e Herzegovina", "BW": "Botsuana", "BR": "Brasil",
    "BN": "Brunei", "BG": "Bulgária", "BF": "Burkina Faso", "BI": "Burundi", "BT": "Butão",
    "CV": "Cabo Verde", "KH": "Camboja", "CM": "Camarões", "CA": "Canadá", "QA": "Catar",
    "KZ": "Cazaquistão", "TD": "Chade", "CZ": "Chéquia", "CL": "Chile", "CN": "China",
    "CY": "Chipre", "CO": "Colômbia", "KM": "Comores", "CG": "Congo-Brazzaville", "CD": "Congo-Kinshasa",
    "KP": "Coreia do Norte", "KR": "Coreia do Sul", "CI": "Costa do Marfim", "CR": "Costa Rica", "HR": "Croácia",
    "CU": "Cuba", "CW": "Curaçao", "DK": "Dinamarca", "DJ": "Djibuti", "DM": "Dominica",
    "EG": "Egito", "SV": "El Salvador", "AE": "Emirados Árabes Unidos", "EC": "Equador", "ER": "Eritreia",
    "SK": "Eslováquia", "SI": "Eslovênia", "ES": "Espanha", "US": "Estados Unidos", "EE": "Estônia",
    "ET": "Etiópia", "FJ": "Fiji", "PH": "Filipinas", "FI": "Finlândia", "FR": "França",
    "GA": "Gabão", "GM": "Gâmbia", "GH": "Gana", "GE": "Geórgia", "GI": "Gibraltar",
    "GD": "Granada", "GR": "Grécia", "GL": "Groenlândia", "GP": "Guadalupe", "GU": "Guam",
    "GT": "Guatemala", "GG": "Guernsey", "GY": "Guiana", "GF": "Guiana Francesa", "GN": "Guiné",
    "GW": "Guiné-Bissau", "GQ": "Guiné Equatorial", "HT": "Haiti", "HN": "Honduras", "HK": "Hong Kong",
    "HU": "Hungria", "YE": "Iêmen", "CX": "Ilha Christmas", "IM": "Ilha de Man", "NF": "Ilha Norfolk",
    "AX": "Ilhas Aland", "KY": "Ilhas Cayman", "CC": "Ilhas Cocos", "CK": "Ilhas Cook", "FO": "Ilhas Faroé",
    "GS": "Ilhas Geórgia do Sul e Sandwich do Sul", "FK": "Ilhas Malvinas", "MP": "Ilhas Marianas do Norte", "MH": "Ilhas Marshall", "UM": "Ilhas Menores Distantes dos EUA",
    "PN": "Ilhas Pitcairn", "SB": "Ilhas Salomão", "TC": "Ilhas Turks e Caicos", "VG": "Ilhas Virgens Britânicas", "VI": "Ilhas Virgens Americanas",
    "IN": "Índia", "ID": "Indonésia", "IR": "Irã", "IQ": "Iraque", "IE": "Irlanda",
    "IS": "Islândia", "IL": "Israel", "IT": "Itália", "JM": "Jamaica", "JP": "Japão",
    "JE": "Jersey", "JO": "Jordânia", "KW": "Kuwait", "LA": "Laos", "LS": "Lesoto",
    "LV": "Letônia", "LB": "Líbano", "LR": "Libéria", "LY": "Líbia", "LI": "Liechtenstein",
    "LT": "Lituânia", "LU": "Luxemburgo", "MO": "Macau", "MK": "Macedônia do Norte", "MG": "Madagascar",
    "MY": "Malásia", "MW": "Malaui", "MV": "Maldivas", "ML": "Mali", "MT": "Malta",
    "MA": "Marrocos", "MQ": "Martinica", "MU": "Maurício", "MR": "Mauritânia", "YT": "Mayotte",
    "MX": "México", "MM": "Mianmar", "FM": "Micronésia", "MD": "Moldávia", "MC": "Mônaco",
    "MN": "Mongólia", "ME": "Montenegro", "MS": "Montserrat", "MZ": "Moçambique", "NA": "Namíbia",
    "NR": "Nauru", "NP": "Nepal", "NI": "Nicarágua", "NE": "Níger", "NG": "Nigéria",
    "NU": "Niue", "NO": "Noruega", "NC": "Nova Caledônia", "NZ": "Nova Zelândia", "OM": "Omã",
    "NL": "Países Baixos", "PA": "Panamá", "PG": "Papua-Nova Guiné", "PK": "Paquistão", "PY": "Paraguai",
    "PE": "Peru", "PF": "Polinésia Francesa", "PL": "Polônia", "PR": "Porto Rico", "PT": "Portugal",
    "MC": "Mônaco", "KE": "Quênia", "KG": "Quirguistão", "GB": "Reino Unido", "UK": "Reino Unido",
    "CF": "República Centro-Africana", "DO": "República Dominicana", "RO": "Romênia", "RW": "Ruanda", "RU": "Rússia",
    "EH": "Saara Ocidental", "WS": "Samoa", "AS": "Samoa Americana", "BL": "São Bartolomeu", "KN": "São Cristóvão e Névis",
    "SM": "San Marino", "MF": "São Martinho", "PM": "São Pedro e Miquelão", "ST": "São Tomé e Príncipe", "VC": "São Vicente e Granadinas",
    "SH": "Santa Helena", "LC": "Santa Lúcia", "SN": "Senegal", "SLE": "Serra Leoa", "RS": "Sérvia",
    "SC": "Seychelles", "SG": "Singapura", "SX": "Sint Maarten", "SY": "Síria", "SO": "Somália",
    "LK": "Sri Lanka", "SZ": "Eswatini", "SD": "Sudão", "SS": "Sudão do Sul", "SE": "Suécia",
    "CH": "Suíça", "SR": "Suriname", "SJ": "Svalbard e Jan Mayen", "TH": "Tailândia", "TW": "Taiwan",
    "TJ": "Tajiquistão", "TZ": "Tanzânia", "TF": "Territórios Franceses do Sul", "IO": "Território Britânico do Oceano Índico", "PS": "Palestina",
    "TL": "Timor-Leste", "TG": "Togo", "TK": "Tokelau", "TO": "Tonga", "TT": "Trinidad e Tobago",
    "TN": "Tunísia", "TM": "Turcomenistão", "TR": "Turquia", "TV": "Tuvalu", "UA": "Ucrânia",
    "UG": "Uganda", "UY": "Uruguai", "UZ": "Uzbequistão", "VU": "Vanuatu", "VA": "Vaticano",
    "VE": "Venezuela", "VN": "Vietnã", "WF": "Wallis e Futuna", "ZM": "Zâmbia", "ZW": "Zimbábue"
}



# Função auxiliar inteligente para traduzir e padronizar estados/regiões retornados em inglês pela API
def traduzir_estado(estado):
    if not estado:
        return estado

    # 1. Dicionário de tradução direta para regiões e estados internacionais famosos
    traducoes_diretas = {
        "Community of Madrid": "Comunidade de Madrid",
        "Madrid": "Madrid",
        "Catalonia": "Catalunha",
        "Andalusia": "Andaluzia",
        "Galicia": "Galícia",
        "Basque Country": "País Basco",
        "Bavaria": "Baviera",
        "Tyrol": "Tirol",
        "Tuscany": "Toscana",
        "Lombardy": "Lombardia",
        "Veneto": "Vêneto",
        "Rome": "Roma",
        "Lazio": "Lácio",
        "England": "Inglaterra",
        "Scotland": "Escócia",
        "Wales": "País de Gales",
        "Northern Ireland": "Irlanda do Norte",
        "Ile-de-France": "Ilha de França",
        "Florida": "Flórida",
        "California": "Califórnia",
        "New York": "Nova York",
        "Texas": "Texas",
        "Hawaii": "Havaí",
        "North Carolina": "Carolina do Norte",
        "South Carolina": "Carolina do Sul",
        "South Dakota": "Dakota do Sul",
        "North Dakota": "Dakota do Norte",
        "New Mexico": "Novo México",
        "New Jersey": "Nova Jersey",
        "State of Bahia": "Bahia",
        "State of São Paulo": "São Paulo",
        "State of Rio de Janeiro": "Rio de Janeiro",
    }

    if estado in traducoes_diretas:
        return traducoes_diretas[estado]

    # 2. Substituição inteligente de termos comuns de divisões geopolíticas
    termos_comuns = {
        "Community of ": "Comunidade de ",
        "Region of ": "Região de ",
        "State of ": "Estado de ",
        "Province of ": "Província de ",
        "Autonomous Community of ": "Comunidade Autónoma de ",
        "Autonomous Region of ": "Região Autónoma de ",
        "Río Negro Province": "Província do Rio Negro"
    }

    estado_traduzido = estado
    for en, pt in termos_comuns.items():
        if estado_traduzido.startswith(en):
            estado_traduzido = estado_traduzido.replace(en, pt)
            break

    return estado_traduzido


# Função que busca o estado e o nome traduzido da cidade para o Português
def obter_dados_geograficos(cidade):
    url = "http://api.openweathermap.org/geo/1.0/direct"  # Endpoint de geocoding direto
    params = {
        "q": cidade,
        "limit": 5,
        "appid": chave_api_local,
    }
    try:
        resposta = requests.get(url, params=params, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados:
                # Tenta pegar o nome em português dentro de local_names, se não existir, usa o nome padrão
                nome_pt = dados[0].get("local_names", {}).get("pt", dados[0].get("name"))
                estado = dados[0].get("state")
                return nome_pt, estado
    except requests.RequestException:
        pass
    return None, None


# Função que, dado lat e lon, retorna a localização traduzida usando geocoding reverso
def obter_localizacao(lat, lon):
    url_localization = "http://api.openweathermap.org/geo/1.0/reverse"  # Endpoint para geocoding reverso
    params = {
        "lat": lat,
        "lon": lon,
        "appid": chave_api_local,
    }
    try:
        resposta = requests.get(url_localization, params=params, timeout=5)
        if resposta.status_code == 200:
            data = resposta.json()
            if data:
                return data
    except requests.RequestException:
        pass
    return None


# Função que busca dados do clima
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
        params["q"] = "São Paulo"

    try:
        resposta = requests.get(url_clima, params=params, timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
    except requests.RequestException:
        pass

    return None


# Rota principal do site ("/")
@app.route("/", methods=["GET", "POST"])
def index():
    clima = None
    erro = None

    if request.method == "POST":
        cidade = request.form.get("cidade", "").strip()
        print("POST recebido, cidade:", cidade)
        if cidade:
            dados = obter_clima(cidade=cidade)
            print("Dados do clima pelo nome da cidade:", dados)
            if dados:
                clima = extrair_dados_clima(dados)
                # Obtendo o nome traduzido em português e o estado da cidade
                nome_traduzido, estado = obter_dados_geograficos(cidade)
                if nome_traduzido:
                    clima["nome"] = nome_traduzido  # Sobrescreve "London" por "Londres", por exemplo
                
                # Traduz e higieniza o nome do estado antes de enviar para a view
                clima["estado"] = traduzir_estado(estado)
            else:
                erro = "Cidade não encontrada ou erro na API."
        else:
            erro = "Digite uma cidade válida."
    else:
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        print("GET recebido, lat:", lat, "lon:", lon)

        if lat and lon:
            dados = obter_clima(lat=lat, lon=lon)
            print("Dados do clima por lat/lon:", dados)
            if dados:
                clima = extrair_dados_clima(dados)
                localizacao = obter_localizacao(lat, lon)
                if localizacao and len(localizacao) > 0:
                    # Pega o nome traduzido para o Português também no geocoding reverso
                    nome_traduzido = localizacao[0].get("local_names", {}).get("pt", localizacao[0].get("name"))
                    clima["nome"] = nome_traduzido
                    clima["estado"] = traduzir_estado(localizacao[0].get("state"))
                else:
                    clima["estado"] = None
            else:
                localizacao = obter_localizacao(lat, lon)
                if localizacao and len(localizacao) > 0:
                    cidade = localizacao[0].get("name")
                    clima["estado"] = traduzir_estado(localizacao[0].get("state"))
                    if cidade:
                        dados = obter_clima(cidade=cidade)
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
            dados = obter_clima()
            if dados:
                clima = extrair_dados_clima(dados)

    print("Final clima:", clima)
    print("Final erro:", erro)

    return render_template("index.html", clima=clima, erro=erro)


# Função que higieniza e arredonda os dados numéricos antes de mandar ao HTML
def extrair_dados_clima(dados):
    # O método round() remove as casas decimais de forma inteligente
    temp_arredondada = round(dados["main"].get("temp", 0))
    sensacao_arredondada = round(dados["main"].get("feels_like", 0))
    
    # Pega a sigla diretamente dos dados da API
    sigla_pais = dados["sys"].get("country")
    
    # Busca a tradução no nosso dicionário. Se não achar, mantém a sigla original
    pais_traduzido = paises_siglas.get(sigla_pais, sigla_pais)
    
    return {
        "nome": dados.get("name"),
        "estado": dados.get("state"),
        "pais": pais_traduzido,
        "descricao": dados["weather"][0].get("description", "").capitalize(),
        "temp": temp_arredondada,
        "sensacao": sensacao_arredondada,
        "umidade": dados["main"].get("humidity"),
        "vento": dados["wind"].get("speed", 0) * 3.6,
        "icone": dados["weather"][0].get("icon") # Extrai o código do ícone para o JavaScript mudar o fundo
    }


if __name__ == "__main__":
    app.run(debug=True)  # Debug = True para mostrar erros e reiniciar automaticamente
