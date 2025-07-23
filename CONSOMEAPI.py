import requests

# Pega o conselho em inglês
url_advice = "https://api.adviceslip.com/advice"
response = requests.get(url_advice)

if response.status_code == 200:
    data = response.json()
    advice = data['slip']['advice']
    print(f"Conselho original: {advice}")

    # Traduz o conselho para português usando MyMemory API
    url_translate = "https://api.mymemory.translated.net/get"
    params = {
        'q': advice,
        'langpair': 'en|pt'
    }
    response_translate = requests.get(url_translate, params=params)
    if response_translate.status_code == 200:
        result = response_translate.json()
        translated_text = result['responseData']['translatedText']
        print(f"Conselho traduzido: {translated_text}")
    else:
        print("Erro na tradução:", response_translate.status_code)
else:
    print(f"Falha ao acessar a API de conselho. Código: {response.status_code}")
