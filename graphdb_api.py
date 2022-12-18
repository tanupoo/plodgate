from SPARQLWrapper import SPARQLWrapper, JSON, POST, POSTDIRECTLY

def graphdb_make_epr(repository, addr, port):
    return {
        "GET": f"http://{addr}:{port}/repositories/{repository}",
        "POST": f"http://{addr}:{port}/repositories/{repository}/statements",
        }

def graphdb_insert(url: str, sentence: str):
    Q = SPARQLWrapper(endpoint=None, updateEndpoint=url)
    Q.setTimeout(5)
    Q.setMethod(POST)
    Q.setQuery(sentence)
    Q.setRequestMethod(POSTDIRECTLY)
    results = Q.query()
    # XXX
    #print(dir(results.response))
    print("## code", results.response.code)
    print("## status", results.response.status)
    #print("## msg", results.response.msg)
    #print("## read()", results.response.read())
    #print("## reason", results.response.reason)
    print("## headers\n", results.response.headers)
    return True

def graphdb_query(url: str, sentence: str):
    Q = SPARQLWrapper(endpoint=url, updateEndpoint=None)
    Q.setTimeout(5)
    Q.setQuery(sentence)
    Q.setReturnFormat(JSON)
    results = Q.query().convert()
    if len(results["results"]["bindings"]):
        for r in results["results"]["bindings"]:
            print(r)
        return True
    else:
        print("Nothing")
        return False

