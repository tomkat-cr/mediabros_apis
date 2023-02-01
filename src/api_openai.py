# openai_api.py
# 2023-01-24 | CR
import openai

from .utility_general import get_api_standard_response, log_debug, log_warning
from .settings import settings


class openai_defaults:
    PROMPT_MODEL = ''
    OPENAI_MODEL = "text-davinci-003"
    TEMPERATURE = "0.6"
    MAX_TOKENS_MIN = "10"
    MAX_TOKENS_MAX = "2048"


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
    prompt_model=openai_defaults.PROMPT_MODEL,
    openai_model=openai_defaults.OPENAI_MODEL,
    temperature=openai_defaults.TEMPERATURE,
    max_tokens=openai_defaults.MAX_TOKENS_MIN
):
    openai.api_key = settings.OPENAI_API_KEY
    response = get_api_standard_response()
    if not question:
        response['error'] = True
        response['error_message'] = 'ERROR OAI-010:' + \
            'No question supplied'
        return response
    try:
        debug_info = {
            'model': openai_model,
            'prompt': get_prompt_model(prompt_model, question),
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        log_debug(f'>>> openai_api_general.debug_info: {debug_info}')
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
        log_warning(response['error_message'])
        return response

    if debug:
        response['data'] = openai_response
        return response
    try:
        if openai_response.choices[0].text:
            return openai_response.choices[0].text
        else:
            response['data'] = openai_response
            response['error'] = True
            response['error_message'] = 'ERROR OAI-020:' + \
                ' OpenAI response error. No choices text'
            log_warning(response['error_message'])
    except Exception as err:
        response['data'] = openai_response
        response['error'] = True
        response['error_message'] = f'ERROR OAI-025: {str(err)}'
        log_warning(response['error_message'])
    return response


def openai_api_with_defaults(request):
    question = request.get('q')
    debug = request.get('debug', '0')
    prompt_model = request.get('p')
    openai_model = request.get('m')
    temperature = request.get('t')
    max_tokens = request.get('mt')

    prompt_model = openai_defaults.PROMPT_MODEL if prompt_model is None \
        else prompt_model
    openai_model = openai_defaults.OPENAI_MODEL if openai_model is None \
        else openai_model
    temperature = openai_defaults.TEMPERATURE if temperature is None \
        else temperature
    max_tokens = openai_defaults.MAX_TOKENS_MAX if max_tokens is None \
        else max_tokens

    return openai_api_general(
        question,
        debug == '1',
        prompt_model,
        openai_model,
        temperature,
        max_tokens
    )
