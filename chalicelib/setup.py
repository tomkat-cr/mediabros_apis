from setuptools import setup

setup(
    name="mediabros_apis",
    version="1.1.0",
    author="Carlos J. Ramirez",
    author_email="cramirez@mediabros.com",
    description="Mediabros APIs for currency and crypto exchange, " +
                "OpenAI API, and Telegram messaging for APIs error reporting",
    packages=["mediabros_apis"],
    install_requires=[
        "requests",
        "fastapi",
        "a2wsgi",
        "openai",
        'werkzeug',
        '"python-jose[cryptography]"',
        '"passlib[bcrypt]"',
        'wheel',
        'python-multipart',
    ],
    zip_safe=False
)
