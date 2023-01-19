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
            if '$ref' in field['items']:
                print('NESTED = ', field)
                nested_name = field['items']['$ref'].split('/')[-1]
                nested_schema = self.model.schema()['definitions'][nested_name]
                print('NESTED SCHEMA= ', nested_schema)
                return self.produce(nested_schema['properties'], 2)
            if field['items']['type'] == 'string':
                return self.faker.pylist(2, True, 'str')
            if field['items']['type'] == 'object':
                return [self.faker.pydict(2, False, 'str') for _ in range(2)]

    def produce(self, schema: dict, count: int) -> list[BaseOrJsonModel]:
        """Produces and records a list of requested models"""
        result = []
        for i in range(count):
            item = {}
            for field in schema.keys():
                item.update({field: self.make_field(schema[field])})
            result.append(item)
        return result

    def inflate(self, count) -> list[BaseOrJsonModel]:
        """Fills top-level model procudtion"""

        # get top level pydantic fields names
        schema = self.model.schema()['properties']
        self.product = self.produce(schema, count)

    def actions(self) -> Generator[dict, None, None]:
        """Issues produced models as ES actions list for bulk execution"""
        for one in self.product:
            yield {"_index": self.index, "_id": one['id'], "_source": one}

    def production(self) -> Generator[dict, None, None]:
        """Issues produced models as sorted raw"""
        for one in sorted(self.product, key=lambda x: x['id']):
            yield one
