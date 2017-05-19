"""
Helper mostly for internal use
"""
from ... import logger


def _extend_column_arg_patch():
    """
    Monkey patch for some custom kwargs.
    """
    from sqlalchemy.sql.schema import Column

    _origin_column_init = Column.__init__

    def _extend_attr(self, *args, **kwargs):
        self.unique_attribute = kwargs.pop('unique_attribute', False)
        _origin_column_init(self, *args, **kwargs)

    Column.__init__ = _extend_attr


def _all_leaf(cls):
    subs = cls.__subclasses__()
    return sum([_all_leaf(cls) for cls in subs], []) if subs else [cls]


def _all_leaf_class(cls):
    if cls.__subclasses__():
        return _all_leaf(cls)
    return []


def _get_table_name_dict(dict_):
    _tablename = dict_.get('__tablename__', None)
    _table = dict_.get('__table__', None)
    tablename = _tablename or _table.name
    assert tablename and isinstance(tablename, (str))
    return tablename


def _get_model_name(dict_):
    _alias = dict_.get('__alias__', None)
    _tablename = _get_table_name_dict(dict_)
    modelname = _alias or _tablename
    assert modelname and isinstance(modelname, (str))
    return modelname


def _pluralize(singular):
    # FIXME: it's wrong, totally
    if singular.endswith('y'):
        return "{}ies".format(singular[:-1])
    return "{}s".format(singular) if not singular.endswith('s') else singular  # FIXME


def _format_for_json(data):
    if hasattr(data, 'as_dict'):
        return data.as_dict()
    elif isinstance(data, (int, float, str)):
        return data
    elif isinstance(data, dict):
        return dict([(k, _format_for_json(v)) for k, v in data.items()])
    elif hasattr(data, '__iter__'):
        return [_format_for_json(_value) for _value in data]
    else:
        return str(data)


class _Jsonable(object):
    # pylint: disable=no-member
    def as_dict(self, only=None, exclude=None, extra=None):
        """
        Format a model instance into json.
        """
        return dict([(_c.name, _format_for_json(getattr(self, _c.name)))
                     for _c in
                     only or set(self.__table__.columns + (extra or [])) - set(exclude or [])])


def _lazy_property(fn):
    lazy_name = '__lazy__' + fn.__name__

    @property
    def lazy_eval(self):
        if not hasattr(self, lazy_name):
            setattr(self, lazy_name, fn(self))
        return getattr(self, lazy_name)
    return lazy_eval