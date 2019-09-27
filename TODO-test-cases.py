class FooItem(Item):
    def __init__(self, value: int, slug: str, display: Optional[str] = None, bar: bool = False):
        super().__init__(value, slug, display)
        self.bar = bar

class FooEnumBase(Enum):
    def something(self) -> FooItem:
        return self.SOMETHING

    def bars(self) -> Sequence[FooItem]:
        return [x for x in self if x.bar]

others = [
    FooItem(100, 'other', bar=True),
]

FooEnum = FooEnumBase('FooEnum',
    FooItem(10, 'something'),
    *others
)
