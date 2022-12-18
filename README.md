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

## test



