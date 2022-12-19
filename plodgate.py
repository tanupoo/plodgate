#!/usr/bin/env python

import asyncio
import aiohttp
from fastapi import FastAPI, Query, Request, Header, status
from fastapi.exceptions import RequestValidationError # debug
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import Required
from plodgate_api import PatientInfoContainer, PatientInfo
from graphdb_api import graphdb_make_epr, graphdb_insert, graphdb_query
from ffhs2plod import ffhs2plod
from sentences import Sentences
import json
import re
import logging


app = FastAPI()


re_date = re.compile("\d{4}-\d{2}-\d{2}")

@app.get("/v1/query")
async def task_get(
        n: str = Query(None, description="query name")
        ) -> dict:
    if n:
        return S.gets(n)
    else:
        return S.list()


@app.post("/v1/query")
async def task_get(
        q: str = Query(Required,
                       description="Query name, identify the query template.",
                       regex="^[\w\d\-]+$"),
        s: str = Query(None,
                       description="Date string, tell data since this date.",
                       regex="^\d{4}-\d{2}-\d{2}$"),
        u: str = Query(None,
                       description="Date string, tell data until this date.",
                       regex="^\d{4}-\d{2}-\d{2}$"),
        p: str = Query(Required,
                       description="Patient ID, identify a patient.",
                       regex="^[\w\d\-]+")):
    # (q)uery_name=<name>
    # (s)ince=YYYY-mm-dd
    # (u)ntil=YYYY-mm-dd
    # (p)atient=uuid
    print(q)
    print(s)
    print(u)
    print(p)
    return [{ "get": 1 }]


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    content = jsonable_encoder(exc.errors())
    logger.error(f"Validation Error: {content}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": content},
    )

@app.post("/v1/insert")
async def task_post(data: PatientInfoContainer):
    plod_text = ffhs2plod(data.__root__)
    if opt.debug:
        logger.debug(plod_text)
    #
    # XXX non async
    if opt.no_harm:
        return plod_text
    else:
        return graphdb_insert(url, plod_text)



#
# main
#
if __name__ == '__main__':
    from uvicorn import Config, Server
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument("--host", "-a",
                    action="store", dest="server_addr",
                    default="0.0.0.0",
                    help="server's IP address to be bound.")
    ap.add_argument("--port", "-p",
                    action="store", dest="server_port",
                    type=int, default=8008,
                    help="server's port number to be listened.")
    ap.add_argument("--graphdb-addr", "-A",
                    action="store", dest="graphdb_addr",
                    default="127.0.0.1",
                    help="GraphDB's IP address.")
    ap.add_argument("--graphdb-port", "-P",
                    action="store", dest="graphdb_port",
                    type=int, default=7200,
                    help="GraphDB's port number.")
    ap.add_argument("graphdb_repository",
                    help="GraphDB's repository.")
    """
    ap.add_argument("--graphdb-repository", "-R",
                    action="store", dest="graphdb_repository",
                    required=True,
                    help="GraphDB's repository.")
    """
    ap.add_argument("--query-repository", "-S",
                    action="store", dest="query_repository",
                    help="directory name containing queries.")
    ap.add_argument("--no-harm",
                    action="store_true", dest="no_harm",
                    help="enable debug mode.")
    ap.add_argument("--debug", "-d",
                    action="store_true", dest="debug",
                    help="enable debug mode.")
    opt = ap.parse_args()
    #
    logger = logging.getLogger("plodgate")
    ch = logging.StreamHandler()
    if opt.debug:
        ch.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    #
    if opt.no_harm:
        logger.info(f"no harm")
    # set initial sentences.
    if opt.query_repository:
        S = Sentences(sentence_repository=opt.query_repository)
    else:
        S = None
    #
    loop = asyncio.new_event_loop()
    graphdb_epr = graphdb_make_epr(opt.graphdb_repository,
                                   opt.graphdb_addr,
                                   opt.graphdb_port)
    server = Server(Config(app=app,
                           host=opt.server_addr,
                           port=opt.server_port,
                           loop=loop,
                           debug=opt.debug))
    loop.run_until_complete(server.serve())


