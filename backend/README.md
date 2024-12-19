# prism backend

## Installation

-----------------

Install Dependencies.

```shell
cd backend
poetry install
```

API Server Local Running.

```shell
python3 -m prism.app
```

## Set up

-----------------

Before use prism setup with the following commands

```shell
cp prism/.env.example prism/.env
```

After running, you can Set your own OPENAPI_API_KEY etc. configration in .env file

## Backend Features List

-----------------

- Fully asynchronous
- Built-in observability based on Opentelemetry
- Funny large model operator development experience based on langchain/langgraph encapsulation