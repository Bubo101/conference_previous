from json import JSONEncoder
from django.db.models import QuerySet
from datetime import datetime


class DateEncoder(JSONEncoder):
    def default(self, o):
        # overriding default method
        if isinstance(o, datetime):
            # ifinstance of object is a datetime format
            return o.isoformat()
            # return object in isoformat which Json can read
        else:
            return super().default(o)
            # returns null (JS for None)


class QuerySetEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet):
            # if instance of object is a queryset
            return list(o)
            # convert queryset into list
        else:
            return super().default(o)


class ModelEncoder(DateEncoder, QuerySetEncoder, JSONEncoder):
    encoders = {}
    # need to create encoder dictionary in case encoder gets used
    def default(self, o):
        if isinstance(o, self.model):
            # if o is the same class/type as self.model
            d = {}
            if hasattr(o, "get_api_url"):
                # if object has url attribute
                d["href"] = o.get_api_url()
                # create a dictionary entry with key "href" and value of url
            for property in self.properties:
                # for property in properties
                value = getattr(o, property)
                # value = object attribute
                if property in self.encoders:
                    # if property name is in an encoder tied to the class
                    encoder = self.encoders[property]
                    value = encoder.default(value)
                d[property] = value
            d.update(self.get_extra_data(o))
            return d
        else:
            return super().default(o)

    def get_extra_data(self, o):
        return {}
