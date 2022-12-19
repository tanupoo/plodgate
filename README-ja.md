plodgate
========

## DBCL GraphDB

テスト用インスタンス: PLOD-test

## FFHSからPLODへの入力チェック

plodgate-api.py: PatientInfoContainerモデルで定義する。

```
python ffhs2plod.py test/test-test-1.json
python test/test-ffhs2plod.py
pytest test/test-ffhs2plod.py
```

## plodgate

起動

```
python plodgate.py --host 127.0.0.1 --port 8000 \
    --graphdb-addr 127.0.0.1 --graphdb-port 7200 \
    --query-repository queries \
    --no-harm --debug \
    PLOD-test
```

## insert

/v1/insert

./client.py --insert test/test-list-1.json http://localhost:8000/v1/insert

## query

/v1/query

./client.py --query queries/query4.txt  http://localhost:8000/v1/query

## template

./client.py http://localhost:8000/v1/template
./client.py http://localhost:8000/v1/template?qid=q1
./client.py --template 'http://localhost:8000/v1/template?qid=q1&pid=taro&since=2022-12-01'

## test



