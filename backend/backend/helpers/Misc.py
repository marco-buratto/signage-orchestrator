import collections


class Misc:
    @staticmethod
    def toDict(layer):
        r = layer
        if isinstance(layer, collections.OrderedDict):
            r = dict(layer)

        try:
            for key, value in r.items():
                r[key] = Misc.toDict(value)
        except AttributeError:
            pass

        return r



    @staticmethod
    def deepRepr(o) -> dict:
        try:
            r = dict()

            try:
                v = vars(o)
            except TypeError:
                v = o

            if isinstance(v, dict):
                for key, val in v.items():
                    if isinstance(val, str) or isinstance(val, int) or isinstance(val, bool):
                        r[key] = val

                    elif isinstance(val, list):
                        if key not in r:
                            r[key] = list()

                        for j in val:
                            r[key].append(Misc.deepRepr(j))

                    else:
                        if key not in r:
                            r[key] = dict()
                        r[key] = Misc.deepRepr(val)
        except Exception as e:
            raise e

        return r
