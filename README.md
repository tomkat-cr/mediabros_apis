# Mediabros APIs

![Mediabros APIs Banner](./assets/mediabros.apis.banner-010.png)

[English](#english) | [Español](#español)

[![Version](https://img.shields.io/badge/version-1.1.1-blue.svg)](https://github.com/tomkat-cr/cop-exchange-rates)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## English

`mediabros_apis` is a serverless application built with Python using the Chalice and FastAPI frameworks. It provides a set of APIs for various functionalities, including currency exchange rate lookups, integration with the OpenAI API and Telegram messaging for APIs error reporting. The project is configured for deployment on AWS Lambda using the Serverless Framework. It's used as a backend API for Telegram and WhatsApp BOTs.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Test API](#test-api)
- [Production API](#production-api)
- [License](#license)
- [Contributing](#contributing)

## Features

- Serverless architecture with AWS Chalice
- API endpoints for currency exchange (Crypto, USD/COP, USD/VEB, etc.)
- Integration with OpenAI's API
- Telegram messaging for APIs error reporting
- JWT-based authentication
- Comprehensive test suite with `pytest`

## Technologies

- **Backend:** Python, Chalice, FastAPI, Pydantic
- **Serverless:** AWS Lambda, Serverless Framework
- **Database/Cache:** MongoDB
- **Testing:** `pytest`, `pytest-chalice`
- **Dependencies:** `boto3`, `python-jose`, `requests`
- **Node.js:** Used for development tools and scripts.

## Getting Started

### Prerequisites

- Python 3.9 - 3.13
- Node.js v20
- Pipenv
- Git
- Make
- Optional (and recommended): Pyenv
- An AWS account and configured credentials

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/mediabros/mediabros_apis.git
    cd mediabros_apis
    ```

2.  **Set up environment variables:**

    Copy the example environment file and fill in your credentials.

    ```bash
    cp .env-example .env
    ```

3.  **Install dependencies:**

    Use the `Makefile` to install both Python and Node.js dependencies.

    ```bash
    make install
    ```

## Usage

This project uses a `Makefile` to streamline common development tasks.

-   **Run the application locally:**

    ```bash
    make run
    ```

-   **Run tests:**

    ```bash
    make test
    ```

-   **Deploy to QA:**

    ```bash
    make deploy
    ```

-   **Deploy to production:**

    ```bash
    make deploy_prod
    ```

-   **Clean up project files:**

    ```bash
    make clean
    ```

-   **Update dependencies:**

    ```bash
    make update
    ```

For a full list of commands, you can inspect the `Makefile`.

## API Endpoints

- `usdcop`: USD to Colombian Pesos (COP)
- `usdveb`: USD to Venezuelan Bolívar (Bs)
- `usdveb_monitor`: USD to Venezuelan Bolívar (Bs) with Monitor rate
- `usdveb_full`: USD to Venezuelan Bolívar (Bs) with official BCV and Monitor rate
- `copveb`: COP to Bs
- `vebcop`: Bs to COP
- `btc`: Bitcoin to USD
- `eth`: Ethereum to USD
- `crypto/{symbol}`: Any crypto currency to USD
- `ai`: Question to OpenAI's ChatGPT
- `codex`: Question to OpenAI's Codex

# Test API

USD to Venezuelan Bolívar (Bs):

[http://127.0.0.1:5001/usdveb](http://127.0.0.1:5001/usdveb)<br/>
[http://127.0.0.1:5001/usdveb/1](http://127.0.0.1:5001/usdveb/1)

USD to Venezuelan Bolívar (Bs) with Monitor (non official) rate:

[http://127.0.0.1:5001/usdveb_monitor](http://127.0.0.1:5001/usdveb_monitor)<br/>
[http://127.0.0.1:5001/usdveb_monitor/1](http://127.0.0.1:5001/usdveb_monitor/1)

USD to Venezuelan Bolívar (Bs) with Monitor (non official) and official BCV rate:

[http://127.0.0.1:5001/usdveb_full](http://127.0.0.1:5001/usdveb_full)<br/>
[http://127.0.0.1:5001/usdveb_full/1](http://127.0.0.1:5001/usdveb_full/1)

USD to Colombian Pesos (COP):

[http://127.0.0.1:5001/usdcop](http://127.0.0.1:5001/usdcop)<br/>
[http://127.0.0.1:5001/usdcop/1](http://127.0.0.1:5001/usdcop/1)

COP to Bs:

[http://127.0.0.1:5001/copveb](http://127.0.0.1:5001/copveb)<br/>
[http://127.0.0.1:5001/copveb/{debug}](http://127.0.0.1:5001/copveb/1)

Bs to COP:

[http://127.0.0.1:5001/vebcop](http://127.0.0.1:5001/vebcop)<br/>
[http://127.0.0.1:5001/vebcop/{debug}](http://127.0.0.1:5001/vebcop/1)

Bitcoin to USD:

[http://127.0.0.1:5001/btc](http://127.0.0.1:5001/btc)<br/>
[http://127.0.0.1:5001/btc/{debug}](http://127.0.0.1:5001/btc/1)

Ethereum to USD:

[http://127.0.0.1:5001/eth](http://127.0.0.1:5001/eth)<br/>
[http://127.0.0.1:5001/eth/{debug}](http://127.0.0.1:5001/eth/1)

Any crypto currency to USD:

[http://127.0.0.1:5001/crypto/{symbol}](http://127.0.0.1:5001/crypto/{symbol})<br/>
[http://127.0.0.1:5001/crypto/{symbol}/{debug}](http://127.0.0.1:5001/crypto/{symbol}/1)

Question to OpenAI's ChatGPT:

[http://127.0.0.1:5001/ai?q=xxx](http://127.0.0.1:5001/ai/q=)

### Production API call

The production API URL when deployed to Vercel project named `mediabros-apis`:

[https://mediabros-apis.vercel.app](https://mediabros-apis.vercel.app)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Credits

This project is developed and maintained by [Carlos J. Ramirez](https://github.com/tomkat-cr). For more information or to contribute to the project, visit [Mediabros APIs](https://github.com/tomkat-cr/mediabros_apis).

Happy Coding!

<br/>

------------------------------

## Español

`mediabros_apis` es una aplicación serverless construida con Python usando los frameworks Chalice y FastAPI. Provee un conjunto de APIs para varias funcionalidades, incluyendo consultas de tasas de cambio, integración con la API de OpenAI y mensajería con Telegram para el reporte de errores de las APIs. El proyecto está configurado para despliegue en AWS Lambda usando el Serverless Framework. Es usado como un API backend para BOTs de Telegram y WhatsApp.

## Tabla de Contenido

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Cómo Empezar](#cómo-empezar)
  - [Prerrequisitos](#prerrequisitos)
  - [Instalación](#instalación)
- [Uso](#uso)
- [Endpoints de la API](#endpoints-de-la-api)
- [API de Prueba](#api-de-prueba)
- [API de Producción](#api-de-producción)
- [Licencia](#licencia)
- [Contribuciones](#contribuciones)

## Características

- Arquitectura Serverless con AWS Chalice
- Endpoints de API para cambio de moneda (Crypto, USD/COP, USD/VEB, etc.)
- Integración con la API de OpenAI
- Mensajería con Telegram para reporte de errores de las APIs
- Autenticación basada en JWT
- Suite de pruebas completa con `pytest`

## Tecnologías

- **Backend:** Python, Chalice, FastAPI, Pydantic
- **Serverless:** AWS Lambda, Serverless Framework
- **Base de Datos/Cache:** MongoDB
- **Pruebas:** `pytest`, `pytest-chalice`
- **Dependencias:** `boto3`, `python-jose`, `requests`
- **Node.js:** Usado para herramientas de desarrollo y scripts.

## Cómo Empezar

### Prerrequisitos

- Python 3.9 - 3.13
- Node.js v20
- Pipenv
- Git
- Make
- Opcional (y recomendado): Pyenv
- Una cuenta de AWS y credenciales configuradas

### Instalación

1.  **Clona el repositorio:**

    ```bash
    git clone https://github.com/mediabros/mediabros_apis.git
    cd mediabros_apis
    ```

2.  **Configura las variables de entorno:**

    Copia el archivo de ejemplo y rellena tus credenciales.

    ```bash
    cp .env-example .env
    ```

3.  **Instala las dependencias:**

    Usa el `Makefile` para instalar las dependencias de Python y Node.js.

    ```bash
    make install
    ```

## Uso

Este proyecto usa un `Makefile` para agilizar las tareas comunes de desarrollo.

-   **Ejecutar la aplicación localmente:**

    ```bash
    make run
    ```

-   **Ejecutar pruebas:**

    ```bash
    make test
    ```

-   **Desplegar a QA:**

    ```bash
    make deploy
    ```

-   **Desplegar a producción:**

    ```bash
    make deploy_prod
    ```

-   **Limpiar archivos del proyecto:**

    ```bash
    make clean
    ```

-   **Actualizar dependencias:**

    ```bash
    make update
    ```

Para una lista completa de comandos, puedes inspeccionar el `Makefile`.

## Endpoints de la API

- `usdcop`: USD a Pesos Colombianos (COP)
- `usdveb`: USD a Bolívar Venezolano (Bs)
- `usdveb_monitor`: USD a Bolívar Venezolano (Bs) con tasa Monitor
- `usdveb_full`: USD a Bolívar Venezolano (Bs) con tasa oficial BCV y Monitor
- `copveb`: COP a Bs
- `vebcop`: Bs a COP
- `btc`: Bitcoin a USD
- `eth`: Ethereum a USD
- `crypto/{symbol}`: Cualquier criptomoneda a USD
- `ai`: Pregunta a ChatGPT de OpenAI
- `codex`: Pregunta a Codex de OpenAI

## API de Prueba

USD a Bolívar Venezolano (Bs):

[http://127.0.0.1:5001/usdveb](http://127.0.0.1:5001/usdveb)<br/>
[http://127.0.0.1:5001/usdveb/1](http://127.0.0.1:5001/usdveb/1)

USD a Bolívar Venezolano (Bs) con tasa Monitor (no oficial):

[http://127.0.0.1:5001/usdveb_monitor](http://127.0.0.1:5001/usdveb_monitor)<br/>
[http://127.0.0.1:5001/usdveb_monitor/1](http://127.0.0.1:5001/usdveb_monitor/1)

USD a Bolívar Venezolano (Bs) con tasa Monitor (no oficial) y oficial del BCV:

[http://127.0.0.1:5001/usdveb_full](http://127.0.0.1:5001/usdveb_full)<br/>
[http://127.0.0.1:5001/usdveb_full/1](http://127.0.0.1:5001/usdveb_full/1)

USD a Pesos Colombianos (COP):

[http://127.0.0.1:5001/usdcop](http://127.0.0.1:5001/usdcop)<br/>
[http://127.0.0.1:5001/usdcop/1](http://127.0.0.1:5001/usdcop/1)

COP a Bs:

[http://127.0.0.1:5001/copveb](http://127.0.0.1:5001/copveb)<br/>
[http://127.0.0.1:5001/copveb/{debug}](http://127.0.0.1:5001/copveb/1)

Bs a COP:

[http://127.0.0.1:5001/vebcop](http://127.0.0.1:5001/vebcop)<br/>
[http://127.0.0.1:5001/vebcop/{debug}](http://127.0.0.1:5001/vebcop/1)

Bitcoin a USD:

[http://127.0.0.1:5001/btc](http://127.0.0.1:5001/btc)<br/>
[http://127.0.0.1:5001/btc/{debug}](http://127.0.0.1:5001/btc/1)

Ethereum a USD:

[http://127.0.0.1:5001/eth](http://127.0.0.1:5001/eth)<br/>
[http://127.0.0.1:5001/eth/{debug}](http://127.0.0.1:5001/eth/1)

Cualquier criptomoneda a USD:

[http://127.0.0.1:5001/crypto/{symbol}](http://127.0.0.1:5001/crypto/{symbol})<br/>
[http://127.0.0.1:5001/crypto/{symbol}/{debug}](http://127.0.0.1:5001/crypto/{symbol}/1)

Pregunta a ChatGPT de OpenAI:

[http://127.0.0.1:5001/ai?q=xxx](http://127.0.0.1:5001/ai/q=)

## API de Producción

La URL de la API de producción cuando se despliega en el proyecto de Vercel llamado `mediabros-apis`:

[https://mediabros-apis.vercel.app](https://mediabros-apis.vercel.app)

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

### Contribuciones

¡Las contribuciones son bienvenidas! No dudes en enviar un pull request o abrir un issue si tienes alguna sugerencia o encuentras algún error.

## Créditos

Este proyecto es desarrollado y mantenido por [Carlos J. Ramirez](https://github.com/tomkat-cr). Para más información o para contribuir al proyecto, visite [Mediabros APIs](https://github.com/tomkat-cr/mediabros_apis).

¡Sé Feliz Programando!
