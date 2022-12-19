from pydantic import BaseModel
from typing import Optional
import os
import glob
import re

re_name = re.compile("^#%name:(.*)")
re_desc = re.compile("^#%desc:(.*)")

class QuerySentence(BaseModel):
    name: str   # unique
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

    def _gets(self, name):
        for x in self.S:
            if x.name == name:
                return x
        else:
            raise ValueError(f"ERROR: not found for name={name}")

    def title(self, name):
        self._gets(name).title

    def text(self, name):
        self._gets(name).text

    def print(self, name=None, verbose=False):
        if verbose:
            fmt = "## {name}: {desc}\n{text}"
        else:
            fmt = "## {name}: {desc}"
        if name:
            print(fmt.format(**(self._gets(name).dict())))
        else:
            for x in self.S:
                print(fmt.format(**(x.dict())))

    def gets(self, name):
        return self._gets(name).dict()

    def list(self):
        ret = []
        for x in self.S:
            ret.append(x.dict())
        return ret
