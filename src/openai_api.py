# openai_api.py
# 2023-01-24 | CR
import openai

from .general_utilities import get_api_standard_response
from .settings import settings


def get_prompt_model(prompt_model, question):
    response = question
    if prompt_model == 'title_suggestion':
        response = """Suggest five titles for a blog post about APIs.

API: currency exchange rate
Titles:\n1. How to Utilize VEB, COP and Crypto Currencies with a Currency Exchange Rate API\n2. Exploring the Benefits of a Currency Exchange Rate API for VEB, COP and Crypto Currencies\n3. Unlocking the Potential of VEB, COP and Crypto Currencies with a Currency Exchange Rate API\n4. Understanding the Power of a Currency Exchange Rate API for VEB, COP and Crypto Currencies\n5. Making the Most of Your VEB, COP and Crypto Currencies with a Currency Exchange Rate API
API: Telegram BOT
Titles: 1. How to make a Telegram BOT API\n2. Exploring the Benefits of a Telegram BOT\n3. Unlocking the Potential of Telegram BOT API\n4. Understanding the Power of a Telegram BOT API\n5. Making the Most of Your Telegram BOT API
API: {}
Titles:""".format(question.capitalize())
    return response


def openai_api_general(
    question,
    debug=False,
    prompt_model='',
    openai_model="text-davinci-003",
    temperature=0.6,
    max_tokens=10
):
    openai.api_key = settings.OPENAI_API_KEY
    response = get_api_standard_response()
    if question == '':
        response['error'] = True
        response['error_message'] = 'ERROR OAI-010:' + \
            'No question supplied'
        return response
    try:
        openai_response = openai.Completion.create(
            model=openai_model,
            prompt=get_prompt_model(prompt_model, question),
            temperature=float(temperature),
            max_tokens=int(max_tokens),
        )
        openai_response['question'] = question
    except Exception as err:
        response['error'] = True
        response['error_message'] = f'ERROR OAI-030: {str(err)}'
        print(response['error_message'])
        return response

    if debug:
        response['data'] = openai_response
        return response
    try:
        if openai_response.choices[0].text:
            response['data'] = openai_response.choices[0].text
        else:
            response['data'] = openai_response
            response['error'] = True
            response['error_message'] = 'ERROR OAI-020:' + \
                ' OpenAI response error. No choices text'
            print(response['error_message'])
    except Exception as err:
        response['data'] = openai_response
        response['error'] = True
        response['error_message'] = f'ERROR OAI-025: {str(err)}'
        print(response['error_message'])
    return response


def openai_api_with_defaults(request):
    question = request.get('q')
    debug = request.get('debug', '0')
    prompt_model = request.get('p', '')
    openai_model = request.get('m', 'text-davinci-003')
    temperature = request.get('t', '0.6')
    max_tokens = request.get('mt', '2048')
    return openai_api_general(
        question,
        debug,
        prompt_model,
        openai_model,
        temperature,
        max_tokens
    )
