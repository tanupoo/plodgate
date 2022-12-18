from pydantic import BaseModel
from typing import Optional
import os
import glob
import re

re_name = re.compile("^#%name:(.*)")
re_desc = re.compile("^#%desc:(.*)")

class QuerySentence(BaseModel):
    name: str
    desc: Optional[str]
    text: str

class Sentences:

    def __init__(self, sentence_list=None, sentence_repository=None,
                 glob_str="*.txt"):
        self.S = []
        if sentence_list:
            for i,x in enumerate(sentence_list):
                self.S.append(QuerySentence.parse_obj(x))
        elif sentence_repository:
            # XXX needs to be improved.
            for f in glob.glob(os.path.join(sentence_repository, glob_str)):
                with open(f) as fd:
                    name = None
                    desc = None
                    text = []
                    for line in fd:
                        r = re_name.match(line)
                        if r:
                            name = r.group(1).strip()
                            continue
                        r = re_desc.match(line)
                        if r:
                            desc = r.group(1).strip()
                            continue
                        text.append(line)
                    self.S.append(QuerySentence(name=name, desc=desc,
                                                text="".join(text)))
        else:
            # if not (sentence_list or sentence_repository):
            raise ValueError("Either sentence_list or sentence_repository is required.")

    def title(self, tid):
        for x in self.S:
            if x["id"] == tid:
                return x["title"]
        else:
            raise ValueError("ERROR: no text found for id={tid}")

    def text(self, tid):
        for x in self.S:
            if x["id"] == tid:
                return x["text"]
        else:
            raise ValueError("ERROR: no text found for id={tid}")

    def list(self, verbose=False):
        if verbose:
            fmt = "## {name}: {desc}\n{text}"
        else:
            fmt = "## {name}: {desc}"
        for x in self.S:
            print(fmt.format(**(x.dict())))

