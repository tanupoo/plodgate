plodgate
========

## requirement

- aiohttp
- fastapi
- SPARQLWrapper
- uvicorn

## Architecture

```
|client|<-- -->|plodgate|<-- -->|GraphDB|
```

```
A: --host, --port
B: --graphdb-addr, --graphdb-port
```

## plodgate

起動

```
python plodgate.py --host 127.0.0.1 --port 8000 \
    --graphdb-addr 127.0.0.1 --graphdb-port 7200 \
    --query-repository queries \
    --no-harm --debug \
    PLOD-DB
```

## insert

/v1/insert

```
./client.py --insert test/test-list-1.json http://localhost:8000/v1/insert
```

```
curl -X POST -d @test/test-list-1.json -H 'Content-Type: application/json' http://localhost:8000/v1/insert
```

## query

/v1/query

```
./client.py --query queries/query4.txt  http://localhost:8000/v1/query
```

```
curl -X POST -d @queries/query4.txt -H 'Content-Type: plain/text' http://localhost:8000/v1/query
```

## template

```
./client.py http://localhost:8000/v1/template
./client.py http://localhost:8000/v1/template?qid=q1
./client.py --template 'http://localhost:8000/v1/template?qid=q1&pid=taro&since=2022-12-01'
```

```
curl http://localhost:8000/v1/template
curl http://localhost:8000/v1/template?qid=q1
curl -X POST 'http://localhost:8000/v1/template?qid=q1&pid=taro&since=2022-12-01'
```

## test

