# openai_api.py
# 2023-01-24 | CR
import json
import openai
import requests

from chalicelib.utility_general import \
    get_api_standard_response, log_debug, log_warning
from chalicelib.settings import settings


class openai_defaults:
    PROMPT_MODEL = ''
    # OPENAI_MODEL = "text-davinci-003"
    OPENAI_MODEL = "gpt-4"
    TEMPERATURE = "1"
    MAX_TOKENS_MIN = "10"
    MAX_TOKENS_MAX = "2048"
    API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


def adjust_prompt(prompt_model, messages):
    response = get_api_standard_response()
    if not messages:
        response['error'] = True
        response['error_message'] = 'ERROR OAI-050:' + \
            'No question supplied'
        return response
    if messages[0] == '{':
        try:
            response['messages'] = json.loads(messages)
            return response
        except Exception as err:
            response['error'] = True
            response['error_message'] = 'ERROR OAI-060:' + \
                f'Cannot json decode question: {str(err)}'
            return response
    else:
        response['messages'] = None

    if prompt_model == 'esp_eng_translation':
        response['messages'] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Translate the following Spanish" +
                f" text to English: '{str(response['messages'])}'"},
        ]

    if prompt_model == 'eng_fr_translation':
        response['messages'] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Translate the following English" +
                f" text to French: '{str(response['messages'])}'"},
        ]

    if response['messages'] is None:
        response['messages'] = [
            {"role": "user", "content": str(messages)},
        ]

    return response


def openai_api_general(
    messages,
    debug=False,
    prompt_model=openai_defaults.PROMPT_MODEL,
    openai_model=openai_defaults.OPENAI_MODEL,
    temperature=openai_defaults.TEMPERATURE,
    max_tokens=None
):
    response = get_api_standard_response()
    if not messages:
        response['error'] = True
        response['error_message'] = 'ERROR OAI-010:' + \
            'No question supplied'
        return response
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        }
        prompt = adjust_prompt(prompt_model, messages)
        if not prompt['error']:
            return prompt
        data = {
            "model": openai_model,
            "messages": prompt['messages'],
            "temperature": temperature,
        }
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        log_debug(f'>>> openai_api_general.data: {data}')
        http_response = requests.post(
            openai_defaults.API_ENDPOINT,
            headers=headers,
            data=json.dumps(data)
        )
        if http_response.status_code == 200:
            openai_response = http_response.json()
            openai_response['question'] = messages
        else:
            # raise Exception(f"Error {response.status_code}: {response.text}")
            response['error'] = True
            response['error_message'] = 'ERROR OAI-040: Status Code:' + \
                f' {response.status_code}' + \
                f'| Msg: {response.text}'
            log_warning(response['error_message'])
            return response

    except Exception as err:
        response['error'] = True
        response['error_message'] = f'ERROR OAI-030: {str(err)}'
        log_warning(response['error_message'])
        return response

    if debug:
        response['data'] = openai_response
        return response
    try:
        if openai_response["choices"][0]["message"]["content"]:
            return openai_response["choices"][0]["message"]["content"]
        else:
            response['data'] = openai_response
            response['error'] = True
            response['error_message'] = 'ERROR OAI-020:' + \
                ' OpenAI response error. No choices message content'
            log_warning(response['error_message'])
    except Exception as err:
        response['data'] = openai_response
        response['error'] = True
        response['error_message'] = f'ERROR OAI-025: {str(err)}'
        log_warning(response['error_message'])
    return response


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


def openai_api_general_oai_lib(
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
        # https://platform.openai.com/docs/api-reference/completions/create
        # POST https://api.openai.com/v1/completions
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
    # max_tokens = openai_defaults.MAX_TOKENS_MAX if max_tokens is None \
    #     else max_tokens

    return openai_api_general(
        question,
        debug == '1',
        prompt_model,
        openai_model,
        temperature,
        max_tokens
    )
