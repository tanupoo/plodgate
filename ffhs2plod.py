from plodgate_api import PatientInfoContainer, PatientInfo
from datetime import datetime
from rdflib import Graph, BNode, Literal
from rdflib.namespace import Namespace
from hashlib import sha256  # used in get_evid()
from random import random   # used in get_evid()
import re   # used in make_namespaces()

def make_namespaces(G, ns_lines=None, debug=False):
    class _NS:
        def add(self, attr, ns):
            self.__dict__.update({attr:ns})
        def get(self, attr):
            return getattr(self, attr)
    #
    NS = _NS()
    if ns_lines:
        re_prefix = re.compile("(\s+):")
        re_uri = re.compile("<(\s+)>")
        #
        for x in ns_lines.split("\n"):
            x = x.strip()
            if len(x) > 0:
                tag, name, uri = x.split()[:3]
                r_name = re.match("(\w+):", name)
                r_uri = re.match("<([^\s]+)>", uri)
                if not (r_name and r_uri):
                    print(f"ERROR: {name} or {uri} doesn't look like a prefix.")
                    exit(1)
                name = r_name.group(1)
                uri = r_uri.group(1)
                if debug:
                    print(f"DEBUG: NS: {name} = {uri}")
                NS.add(name, Namespace(uri))
                G.bind(name, NS.get(name))
    return NS

# is it okey to just use BNode() ??
def get_evid():
	max_keysize = 32
	h = sha256()
	h.update(f"{str(datetime.now())}{random()}".encode())
	return f"event-{h.hexdigest()[:max_keysize]}"

#
#
#
"""
e.g. input_data in JSON

{
    "event_id": "1",
    "when": "お昼ごろ",
    "time": "13:00頃",
    "duration": "1時間",
    "where": "イトーヨーカドー大森店",
    "coordinates": "",
    "what": "買い物",
    "detail": "",
    "who": "妻、息子、義父",
    "other": "移動は自家用車",
}

plod:{eventId} a schema:Event,
        owl:NamedIndividual ;
    rdfs:label "イベント{eventId}:{when}{where}{what}"@ja ;
    time:hasPossibleBeginning plod:{time or when} ;
    time:hasDuration plod:{duration} ;
    schema:location plod:{where} ;
    plod:action plod:{what};
    plod:agent plod:{who[0]},
               plod:{who[1]},
               ... ;
    plod:situationOfActivity plod:facetoface,
        plod:prolongedContact ;
    rdfs:comment "{other}"@ja ;
"""

def init_graph(debug: bool=False):
    G = Graph()
    NS = make_namespaces(G, ns_lines="""
        @prefix hutime: <http://resource.hutime.org/ontology/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix plod: <http://plod.info/rdf/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix schema: <http://schema.org/> .
        @prefix time: <http://www.w3.org/2006/time#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        """, debug=debug)
    return G, NS

def _convert(input_data: PatientInfoContainer, debug: bool=False):
    G, NS = init_graph(debug)
    for dx in input_data.__root__:
        if not dx.event_id:
            evid = get_evid()   # eventId
        else:
            evid = dx.event_id
        #
        ev = NS.plod.term(f"{evid}")
        G.add((ev, NS.rdf.type, NS.schema.Event))
        G.add((ev, NS.rdf.type, NS.owl.NamedIndividual))
        # rdfs:label
        label = f"イベント{evid}:"
        label += "{}{}{}".format(dx.when, dx.where, dx.what)
        G.add((ev, NS.rdfs.label, Literal(label, lang="ja")))

        if dx.duration:
            G.add((ev, NS.time.hasDuration, NS.plod.term(dx.duration)))
        # time:...
        if dx.time:
            G.add((ev, NS.time.hasPossibleBeginning, NS.plod.term(dx.time)))
        elif dx.when:
            G.add((ev, NS.time.hasPossibleBeginning, NS.plod.term(dx.when)))
        else:
            G.add((ev, NS.time.hasPossibleBeginning, NS.plod.term("わからない")))

        # schema:location
        """
        @XXX plod:location
        - whereの空白文字の扱いは？
        """
        if dx.where:
            #dx.where = dx.where.replace(" ","")
            if dx.where.find(" "):
                G.add((ev, NS.schema.location, Literal(dx.where, lang="ja")))
            else:
                G.add((ev, NS.schema.location, NS.plod.term(dx.where)))

        # plod.agent
        """
        @XXX plod:agent
        - patient_idをwho[0]にセットする。
        - whoに複数いることを判定したい。
        - whoを分割するいい方法はないか？
        - who にコメントが入っている。
        """
        who_list = [dx.patient_id] + dx.who.replace("、",",").split(",")
        if len(who_list) > 0:
            for w in who_list:
                G.add((ev, NS.plod.agent, NS.plod.term(w)))

        # plod.action
        """
        - plod:removeMaskなどactionの補足をどうするか？
        - plod:situationOfActivityなどactionの補足をどうするか？
        """
        if dx.what:
            G.add((ev, NS.plod.action, NS.plod.term(dx.what)))
        #G.add((ev, NS.plod.action, NS.plod.removeMask))
        #G.add((ev, NS.plod.action, NS.plod.talk))
        #G.add((ev, NS.plod.situationOfActivity, NS.plod.facetoface))
        #G.add((ev, NS.plod.situationOfActivity, NS.plod.prolongedContact))
        if dx.other:
            G.add((ev, NS.rdfs.comment, Literal(dx.other, lang="ja")))

    return G

def ffhs2plod(ffhs_data: PatientInfoContainer,
              loosy: bool=False,
              debug: bool=False
              ) -> dict:
    """
    Convert FFHS 患者データ in JSON into PLOD in RDF turtle.
    Parameters:
        ffhs_data: 患者データ(JSON)のリスト
        loosy: フラグ(XXX 要検討)
        debug: フラグ
    @return: PLOD (RDF turtle)
    """
    if not loosy:
        # XXX 変換対象は？
        # 必要なデータがそろっているかチェックするか？
        # エラーになったデータは？
        pass
    return _convert(PatientInfoContainer.parse_obj(ffhs_data),
                    debug=debug).serialize(format="turtle")

if __name__ == "__main__" :
    import sys
    import json
    from argparse import ArgumentParser
    ap = ArgumentParser(description="""
        convertering the output of kanja info GUI
        into the input for PLOD.
        """)
    ap.add_argument("ffhs_data_file", help="specify an input file. "
                    "'-' as the stdin is acceptable.")
    ap.add_argument("-l", action="store", dest="loosy",
                    help="enable loosy mode.")
    ap.add_argument("--debug", "-d", action="store_true", dest="debug",
                    help="enable debug mode.")
    opt = ap.parse_args()
    #
    if opt.ffhs_data_file == "-":
        input_json = json.load(sys.stdin)
    else:
        input_json = json.load(open(opt.ffhs_data_file))
    print(ffhs2plod(input_json, loosy=opt.loosy, debug=opt.debug))
