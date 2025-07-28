# mediabros_apis

## English

Mediabros APIs are a collection of endpoints to get currency exchange (Colombian Pesos or Venezuelan Bolívar to US Dolar), crypto prices, OpenAI API, and Telegram messaging for APIs error reporting.

### Technologies

- Backend: Python, FastAPI and Chalice
- Database: MongoDB
- API Gateway: AWS API Gateway
- Deployment: AWS Lambda

### APIs

- ai: Question to OpenAI's ChatGPT
- usdcop: USD to Colombian Pesos (COP)
- usdveb: USD to Venezuelan Bolívar (Bs)
- usdveb_monitor: USD to Venezuelan Bolívar (Bs) with Monitor rate
- usdveb_full: USD to Venezuelan Bolívar (Bs) with official BCV and Monitor rate
- copveb: COP to Bs
- vebcop: Bs to COP
- btc: Bitcoin to USD
- eth: Ethereum to USD
- crypto/{symbol}: Any crypto currency to USD

### Requirements

- Python 3.11 - 3.13
- Git
- Pipenv
- Make
- Optional: pyenv

### Usage

To run the API locally:

Clone the repository:

```bash
git clone https://github.com/tomkat-cr/mediabros_apis.git
```
```bash
cd mediabros_apis
```

Install dependencies:

```bash
make install
```

Set the .env file:

```bash
cp .env-example .env
```

Edit the .env file and follow the instructions in the file's comments:

```bash
nano .env
```

Run the API:

```bash
make run
```

To deploy to AWS Lambda and API Gateway:

```bash
make deploy
```

Test API:

USD to Venezuelan Bolívar (Bs):

[http://127.0.0.1:5001/usdveb](http://127.0.0.1:5001/usdveb)<br/>
[http://127.0.0.1:5001/usdveb/1](http://127.0.0.1:5001/usdveb/1)

USD to Colombian Pesos (COP):

[http://127.0.0.1:5001/usdcop](http://127.0.0.1:5001/usdcop)<br/>
[http://127.0.0.1:5001/usdcop/1](http://127.0.0.1:5001/usdcop/1)

### Production API call

The following are production API call examples when deployed to Vercel project named `mediabros-apis`:

Question to OpenAI's ChatGPT:

[https://mediabros-apis.vercel.app/ai?q=xxx](https://mediabros-apis.vercel.app/ai/q=)

USD to Colombian Pesos (COP):

[https://mediabros-apis.vercel.app/usdcop](https://mediabros-apis.vercel.app/usdcop)<br/>
[https://mediabros-apis.vercel.app/usdcop/{debug}](https://mediabros-apis.vercel.app/usdcop/1)

USD to Venezuelan Bolívar (Bs):

[https://mediabros-apis.vercel.app/usdveb](https://mediabros-apis.vercel.app/usdveb)<br/>
[https://mediabros-apis.vercel.app/usdveb/{debug}](https://mediabros-apis.vercel.app/usdveb/1)

COP to Bs:

[https://mediabros-apis.vercel.app/copveb](https://mediabros-apis.vercel.app/copveb)<br/>
[https://mediabros-apis.vercel.app/copveb/{debug}](https://mediabros-apis.vercel.app/copveb/1)

Bs to COP:

[https://mediabros-apis.vercel.app/vebcop](https://mediabros-apis.vercel.app/vebcop)<br/>
[https://mediabros-apis.vercel.app/vebcop/{debug}](https://mediabros-apis.vercel.app/vebcop/1)

Bitcoin to USD:

[https://mediabros-apis.vercel.app/btc](https://mediabros-apis.vercel.app/btc)<br/>
[https://mediabros-apis.vercel.app/btc/{debug}](https://mediabros-apis.vercel.app/btc/1)

Ethereum to USD:

[https://mediabros-apis.vercel.app/eth](https://mediabros-apis.vercel.app/eth)<br/>
[https://mediabros-apis.vercel.app/eth/{debug}](https://mediabros-apis.vercel.app/eth/1)

Any crypto currency to USD:

[https://mediabros-apis.vercel.app/crypto/{symbol}](https://mediabros-apis.vercel.app/crypto/{symbol})<br/>
[https://mediabros-apis.vercel.app/crypto/{symbol}/{debug}](https://mediabros-apis.vercel.app/crypto/{symbol}/1)

<br/>

------------------------------

## Spanish

Mediabros APIs son una serie de endpoints para obtener cotizaciones de moneda (Pesos Colombianos o Bolívares a Dolar Norteamericano), precio de criptomonedas, API de OpenAI, y mensajería Telegram para reporte de errores de las API, entre otros. Este Backend esta hecho en Python y FastAPI.

## Llamada a la API de producción

Pregunta a ChatGPT de OpenAI:
[https://mediabros-apis.vercel.app/ai?q=xxx](https://mediabros-apis.vercel.app/ai/q=)

Cotización del Dólar respecto al Peso Colombiano (COP):
[https://mediabros-apis.vercel.app/usdcop](https://mediabros-apis.vercel.app/usdcop)<br/>
[https://mediabros-apis.vercel.app/usdcop/{debug}](https://mediabros-apis.vercel.app/usdcop/1)

Cotización del Dólar respecto al Bolívar de Venezuela (Bs):
[https://mediabros-apis.vercel.app/usdveb](https://mediabros-apis.vercel.app/usdveb)<br/>
[https://mediabros-apis.vercel.app/usdveb/{debug}](https://mediabros-apis.vercel.app/usdveb/1)

COP a Bs
[https://mediabros-apis.vercel.app/copveb](https://mediabros-apis.vercel.app/copveb)<br/>
[https://mediabros-apis.vercel.app/copveb/{debug}](https://mediabros-apis.vercel.app/copveb/1)

Bs a COP
[https://mediabros-apis.vercel.app/vebcop](https://mediabros-apis.vercel.app/vebcop)<br/>
[https://mediabros-apis.vercel.app/vebcop/{debug}](https://mediabros-apis.vercel.app/vebcop/1)

Cotización del Bitcoin respecto al Dólar
[https://mediabros-apis.vercel.app/btc](https://mediabros-apis.vercel.app/btc)<br/>
[https://mediabros-apis.vercel.app/btc/{debug}](https://mediabros-apis.vercel.app/btc/1)

Cotización del Ethereum respecto al Dólar
[https://mediabros-apis.vercel.app/eth](https://mediabros-apis.vercel.app/eth)<br/>
[https://mediabros-apis.vercel.app/eth/{debug}](https://mediabros-apis.vercel.app/eth/1)

Cotización del cualquer cripto moneda respecto al Dólar
[https://mediabros-apis.vercel.app/crypto/{symbol}](https://mediabros-apis.vercel.app/crypto/{symbol})<br/>
[https://mediabros-apis.vercel.app/crypto/{symbol}/{debug}](https://mediabros-apis.vercel.app/crypto/{symbol}/1)
