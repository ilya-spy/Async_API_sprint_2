from typing import Generator

from faker import Faker
from faker.providers import python

from testdata.models.model import BaseOrJsonModel


class Factory:
    """Basic factory pattern implementation for models generation"""

    def __init__(self, index: str, model: BaseOrJsonModel) -> None:
        self.product = []
        self.model = model
        self.index = index

        Faker.seed(seed=4231)
        self.faker = Faker()
        self.faker.add_provider(python)

    def make_field(self, field: object):
        type = field['type']

        if type == 'number':
            return self.faker.pyint()
        if type == 'string':
            if 'format' in field:
                if field['format'] == 'uuid':
                    return self.faker.uuid4()
            return self.faker.pystr()
        if type == 'float':
            return self.faker.pyfloat()
        if type == 'array':
            if field['items']['type'] == 'string':
                return self.faker.pylist(2, True, 'str')
            if field['items']['type'] == 'object':
                return [self.faker.pydict(2, False, 'str') for _ in range(2)]

    def produce(self, count: int) -> list[BaseOrJsonModel]:
        """Produces and records a list of requested models"""

        # get pydantic fields names
        schema = self.model.schema()['properties']

        for i in range(count):
            item = {}
            for field in schema.keys():
                item.update({field: self.make_field(schema[field])})
            self.product.append(item)
        return self.product

    def actions(self) -> Generator[dict, None, None]:
        """Issues produced models as ES actions list for bulk execution"""
        for one in self.product:
            yield {"_index": self.index, "_id": one['id'], "_source": one}

    def production(self) -> Generator[dict, None, None]:
        """Issues produced models as sorted raw"""
        for one in sorted(self.product, key=lambda x: x['id']):
            yield one
