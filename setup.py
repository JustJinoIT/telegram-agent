from setuptools import setup

setup(
    name="telegram-agent",
    version="0.1.0",
    description="Telegram Agent — FastAPI + Telegram.ext 통합 프레임워크",
    author="JustJino",
    author_email="dogfootbro@gmail.com",
    url="https://github.com/justjiinoit/telegram-agent",
    py_modules=["telegram_agent"],
    python_requires=">=3.9",
    install_requires=[
        "python-telegram-bot>=21.0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-asyncio"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
