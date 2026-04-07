class Digest(dict):

    def __init__(self, *source, **kwargs):
        super().__init__()

        data = {}

        for arg in source:
            if isinstance(arg, dict):
                data.update(arg)

        data.update(kwargs)

        for k, v in data.items():
            self[k] = self._wrap(v)

    def _wrap(self, value):
        if isinstance(value, dict):
            return Digest(value)
        elif isinstance(value, list):
            return [self._wrap(v) for v in value]
        elif isinstance(value, tuple):
            return tuple(self._wrap(v) for v in value)
        return value


    def __getattr__(self, attr):
        if attr not in self:
            raise AttributeError("No attribute '{}' in digest".format(attr))
        return self[attr]

    def __setattr__(self, key, value, allow_digest_wrap=True):
        if allow_digest_wrap:
            value = self._wrap(value)
        self[key] = self._wrap(value)


    def __add__(self, other):
        for k, v in other.items():
            self[k] = self._wrap(v)
        return self

    def unwrap(self) -> dict:
        def unpack(value):
            if isinstance(value, Digest):
                return value.unwrap()
            elif isinstance(value, dict):
                return {k: unpack(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [unpack(v) for v in value]
            elif isinstance(value, tuple):
                return tuple(unpack(v) for v in value)
            else:
                return value

        return {k: unpack(v) for k, v in self.items()}


    @classmethod
    def from_locals(cls, locals: dict, exclude: list[str] = None, ignore_falsies=True):
        exclude = set(exclude) if exclude else set()
        exclude.add("self")
        d = Digest()
        for k, v in locals.items():
            if k in exclude or (ignore_falsies and not v):
                continue
            d[k] = v
        return d

    @classmethod
    def list_of(cls, items: list):
        return list([Digest(i) for i in items])
