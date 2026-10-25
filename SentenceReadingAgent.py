import re


class SentenceReadingAgent:
    """A self-contained lexicon and rule-based reader for simple sentences.

    Original tokens are retained for answers. Internal frames separate subjects,
    actions, objects, and prepositional phrases without external NLP packages.
    """

    NAMES = set("Serena Andrew Bobbie Cason David Farzana Frank Hannah Ida Irene Jim "
                "Jose Keith Laura Lucy Meredith Nick Ada Yeeling Yan".lower().split())
    PEOPLE = set("i you he she we they me him her us them man woman boy girl mother "
                 "father children child people person friend king adult adults men".split())
    DET = set("a an the this that these those some any each every all both no".split())
    POSS = set("my your his her its our their".split())
    AUX = set("be am is are was were been being do does did have has had "
              "will would can could may might must should".split())
    PREP = set("to from at in on under over above below near by with for of "
               "through into onto toward towards behind beside between among "
               "against during before after until since without around off".split())
    ADJ = set("hot other long new little good great low same old small large big high "
              "light own hard far late real white close enough plain main sure usual "
              "young ready red direct black short complete whole best better true early "
              "fast simple less slow cold fine certain dark correct able final green "
              "quick warm free strong special clear full blue deep common gold possible "
              "dry busy cool many much few several tall heavy happy sad beautiful".split())
    ADV = set("very too also just only still never often always again together now "
              "then soon here there well perhaps already really not".split())
    NUM = set("one two three four five six seven eight nine ten eleven twelve "
              "hundred thousand half first second third".split())
    TIME = set("morning night day week month year hour minute second evening "
               "afternoon today tomorrow yesterday noon midnight".split())
    DISTANCE = set("mile foot feet inch yard meter kilometre kilometer".split())
    VERBS = set("use write like make see look go come know call find work take get live show "
                "give think say help turn cause mean differ move tell set want sound play put "
                "read spell add follow act ask change need try build stand grow study learn "
                "plant cover let keep cross start draw leave run press stop open seem begin "
                "walk mark care carry rain eat hear cut watch feel talk pose sing measure "
                "happen order pass remember hold listen travel love serve appear govern pull "
                "notice fall reach fly lead cry wait plan rest drive contain teach develop "
                "sleep produce decide stay force test record wonder laugh miss heat bring "
                "sit fill name send buy ride drink wear become climb jump swim pick "
                "answer return paint cost weigh".split())
    IRREGULAR = dict(zip(
        "brought wrote made saw went came found took got gave thought said told knew "
        "began ran ate heard left held sang drove stood taught slept fell flew led "
        "sat sent bought rode drank wore became swam read done been built kept felt".split(),
        "bring write make see go come find take get give think say tell know "
        "begin run eat hear leave hold sing drive stand teach sleep fall fly lead "
        "sit send buy ride drink wear become swim read do be build keep feel".split()))

    def __init__(self):
        self.forms = {v: v for v in self.VERBS}
        for verb in self.VERBS:
            for suffix in ("s", "es", "ed", "d", "ing"):
                self.forms[verb + suffix] = verb
            if verb.endswith("e"):
                self.forms[verb[:-1] + "ing"] = verb
            if verb.endswith("y"):
                self.forms[verb[:-1] + "ies"] = verb
                self.forms[verb[:-1] + "ied"] = verb
            for suffix in ("ed", "ing"):
                self.forms[verb + verb[-1] + suffix] = verb
        self.forms.update(self.IRREGULAR)
        self.forms.update({"written": "write", "given": "give", "taken": "take",
                           "seen": "see", "known": "know", "eaten": "eat",
                           "gone": "go", "drawn": "draw", "grown": "grow",
                           "spoken": "speak", "driven": "drive", "sung": "sing",
                           "flown": "fly", "fallen": "fall", "worn": "wear"})

    @staticmethod
    def _tokens(text):
        return text.strip().rstrip(".?!").replace("\u2019", "'").split()

    def _lemma(self, word):
        word = word.lower()
        if word in self.forms:
            return self.forms[word]
        if word in {"feet", "men", "children"}:
            return {"feet": "foot", "men": "man", "children": "child"}[word]
        return word[:-1] if word.endswith("s") and not word.endswith("ss") else word

    def _person(self, word):
        return word.lower() in self.NAMES | self.PEOPLE

    def _clean(self, words):
        words = list(words)
        while words and words[0].lower() in self.DET | {"very"}:
            words.pop(0)
        while words and words[-1].lower() in {"and", "or"}:
            words.pop()
        return " ".join(words)

    def _head(self, words):
        candidates = [w for w in words if w.lower() not in
                      self.DET | self.POSS | self.ADV | {"and", "or"}
                      and not w.lower().endswith("'s")]
        nouns = [w for w in candidates if w.lower() not in self.ADJ | self.NUM]
        return (nouns or candidates or [""])[-1]

    def _parse(self, words):
        lower = [w.lower() for w in words]
        verb = len(words)
        for i, word in enumerate(lower[1:], 1):
            if word in self.AUX or word in self.forms:
                prev = lower[i - 1]
                if prev in self.DET | self.POSS or prev.endswith("'s"):
                    continue
                if prev in self.ADJ and word not in self.AUX:
                    continue
                verb = i
                break
        action = verb
        while action < len(words) and lower[action] in self.AUX | self.ADV:
            action += 1
        # Copulas have a nominal/adjectival complement rather than a verb.
        if action == len(words) or lower[action] not in self.forms:
            action = verb
        start = min(action + 1, len(words))
        while start < len(words) and lower[start] in {"not", "been", "being"}:
            start += 1
        phrases, obj_end, i = [], len(words), start
        boundaries = self.PREP | {"when", "because", "if", "while", "every"}
        while i < len(words):
            if lower[i] in boundaries:
                obj_end = min(obj_end, i)
                j = i + 1
                while j < len(words) and lower[j] not in boundaries:
                    j += 1
                phrases.append((lower[i], words[i + 1:j], i))
                i = j
            else:
                i += 1
        obj, indirect = words[start:obj_end], []
        if obj and self._person(obj[0]) and len(obj) > 1:
            if action < len(words) and self._lemma(words[action]) in {
                    "give", "bring", "send", "tell", "show", "write", "buy", "teach", "read"}:
                indirect, obj = obj[:1], obj[1:]
        passive = (verb < action and lower[verb] in {"is", "are", "was", "were", "be", "been"}
                   and not lower[action].endswith("ing"))
        return {"subject": words[:verb], "action": words[action] if action < len(words) else "",
                "object": obj, "indirect": indirect, "phrases": phrases, "passive": passive}

    def solve(self, sentence, question):
        """Return an answer drawn from a simple sentence's semantic frame."""
        words, qwords = self._tokens(sentence), self._tokens(question)
        if not words or not qwords:
            return ""
        lower, q = [w.lower() for w in words], [w.lower() for w in qwords]
        frame, qset = self._parse(words), set(q)
        phrases = frame["phrases"]

        def phrase(preps, person=False):
            for prep in preps:
                for p, value, _ in phrases:
                    if p != prep or not value:
                        continue
                    if value[0].lower() in self.forms and prep == "to":
                        continue
                    if person and not any(self._person(w) for w in value):
                        continue
                    return self._clean(value)
            return ""

        def subject():
            return self._clean([w for w in frame["subject"] if w.lower() != "there"])

        def obj():
            return self._head(frame["object"])

        def quantity(units):
            for i, word in enumerate(lower):
                if self._lemma(word) in units or word in units:
                    start = i
                    while start and (lower[start - 1] in self.NUM or
                                     lower[start - 1].isdigit() or lower[start - 1] == "and"):
                        start -= 1
                    return " ".join(words[start:i + 1])
            return ""

        if q[0] == "when" or "time" in qset:
            for word in words:
                if re.fullmatch(r"\d{1,2}:\d{2}(?:[AaPp][Mm])?", word):
                    return word
            for prep, value, _ in phrases:
                if any(self._lemma(w) in self.TIME for w in value):
                    return ("every " if prep == "every" else "") + self._clean(value)
            return next((w for w in words if w.lower() in self.TIME), phrase(["when", "after", "before"]))

        if q[0] == "whose":
            target = q[1] if len(q) > 1 else ""
            for i, word in enumerate(words):
                if target and target not in lower[i + 1:i + 4]:
                    continue
                if word.lower().endswith("'s"):
                    return word[:-2]
                if word.lower() in self.POSS:
                    return word

        if q[0] in {"who", "whom"}:
            if "with" in qset:
                answer = phrase(["with"], person=True)
                if answer:
                    return answer
                others = [w for w in frame["subject"] if self._person(w) and w.lower() not in qset]
                return " and ".join(others) or subject()
            if q[-1] in {"to", "for", "from"} or q[:2] in [["who", "did"], ["who", "does"], ["who", "do"]]:
                answer = phrase([q[-1]] if q[-1] in {"to", "for", "from"} else ["to", "for"], True)
                if answer:
                    return answer
                if frame["indirect"]:
                    return self._clean(frame["indirect"])
                if frame["passive"]:
                    return subject()
                if any(self._person(w) for w in frame["object"]):
                    return self._clean(frame["object"])
            if q[-1] == "by" or frame["passive"]:
                return phrase(["by"], True) or subject()
            if qset & {w.lower() for w in frame["subject"]} & self.NAMES:
                return self._clean(frame["object"]) or subject()
            return subject()

        if q[0] == "where":
            if "from" in qset:
                return phrase(["from"])
            for prep in ["to", "into", "at", "in", "on", "under", "near", "behind",
                         "above", "over", "between", "by", "through", "from"]:
                for p, value, _ in phrases:
                    if p != prep or not value:
                        continue
                    if any(self._lemma(w) in self.TIME or ":" in w for w in value):
                        continue
                    if p == "to" and value[0].lower() in self.forms:
                        continue
                    if any(w.lower() in self.NAMES for w in value):
                        continue
                    return self._head(value)
            return next((w for w in words if w.lower() in {"home", "here", "there", "north", "south", "east", "west"}), obj())

        if q[0] == "why":
            return phrase(["because"]) or phrase(["for"]) or next(
                ("to " + " ".join(v) for p, v, _ in phrases
                 if p == "to" and v and v[0].lower() in self.forms), "")

        if q[0] == "how" or "color" in qset or "colour" in qset:
            kind = q[1] if len(q) > 1 else ""
            if kind == "far":
                return quantity(self.DISTANCE)
            if kind == "long" and quantity(self.TIME):
                return quantity(self.TIME)
            if kind in {"many", "much"}:
                target = self._lemma(q[2]) if len(q) > 2 else ""
                for i, word in enumerate(lower):
                    if self._lemma(word) == target:
                        j = i - 1
                        while j >= 0 and lower[j] in self.ADJ - {"many", "much", "few", "several"}:
                            j -= 1
                        end = j + 1
                        while j >= 0 and (lower[j] in self.NUM | {"many", "much", "few", "several"} or lower[j].isdigit()):
                            j -= 1
                        if end > j + 1:
                            return " ".join(words[j + 1:end])
                return quantity({"pound"})
            properties = {
                "long": {"short", "long"}, "big": {"big", "large", "small", "little"},
                "large": {"big", "large", "small", "little"},
                "old": {"old", "young", "new"}, "fast": {"fast", "slow", "quick"},
                "tall": {"tall", "short", "high", "low"}, "high": {"high", "low"},
                "heavy": {"heavy", "light"}, "deep": {"deep", "low"},
                "color": {"red", "white", "black", "blue", "green", "gold"},
            }
            if "color" in qset or "colour" in qset:
                kind = "color"
            if kind in properties:
                units = {"old": {"year"}, "tall": {"foot", "inch"},
                         "high": {"foot", "inch"}, "heavy": {"pound"},
                         "deep": {"foot", "inch"}}.get(kind, set())
                measured = quantity(units)
                if measured:
                    return measured
                for i, word in enumerate(lower):
                    if word in qset and word not in self.AUX | self.DET | self.ADJ:
                        # Search leftward through this noun's modifiers first.
                        for j in range(i - 1, max(-1, i - 4), -1):
                            if lower[j] in properties[kind]:
                                return words[j]
                            if lower[j] not in self.ADJ | self.NUM | self.DET | self.ADV:
                                break
                        # Predicate adjective: "the dog is very small".
                        if i + 1 < len(words) and lower[i + 1] in self.AUX:
                            for j in range(i + 2, min(len(words), i + 5)):
                                if lower[j] in properties[kind]:
                                    return words[j]
                for i, word in enumerate(lower):
                    if word in properties[kind]:
                        return words[i]
                return quantity({"year", "foot", "feet", "inch", "pound"})
            if kind == "often":
                return next(("every " + self._clean(v) for p, v, _ in phrases if p == "every"),
                            next((w for w in words if w.lower() in {"always", "often", "never", "once"}), ""))
            for prep, value, _ in phrases:
                if prep in {"by", "with"} and not any(self._person(w) for w in value):
                    return self._clean(value)
            if frame["action"].lower() in {"is", "are", "was", "were", "am"}:
                return self._clean(frame["object"])
            return next((w for w in words if w.lower().endswith("ly")
                         or w.lower() in {"fast", "slow", "well"}), frame["action"])

        if q[0] in {"what", "which"}:
            if q[-1] in self.PREP:
                answer = phrase([q[-1]])
                if answer:
                    return answer
            if len(q) > 1 and q[1] in self.forms and q[1] not in self.AUX:
                return self._head(frame["subject"])
            qverbs = [self._lemma(w) for w in q if w in self.forms]
            if "do" in qset and self._lemma(frame["action"]) not in qverbs:
                return frame["action"]
            if len(q) > 1 and q[1] in {"is", "are", "was", "were"}:
                if not any(w.lower() in qset for w in frame["subject"] if w.lower() not in self.DET):
                    return self._head(frame["subject"])
            return obj() or self._head(frame["subject"])

        return obj() or subject()
