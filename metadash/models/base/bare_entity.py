"""
Helper to define Entity models.
"""
import uuid

from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

from .. import db
from ..types import UUID

from .utils import _get_table_name_dict
from .utils import _format_for_json, _Jsonable
from .entity import MetadashEntity, URN


class BareEntityMeta(type(db.Model)):
    """
    Custom metaclass for creating new BareEntity.
    """
    # pylint: disable=no-self-argument
    def __init__(cls, classname, bases, dict_):
        if classname == "BareEntityModel":
            type.__init__(cls, classname, bases, dict_)
            return

        super(BareEntityMeta, cls).__init__(classname, bases, dict_)
        MetadashEntity.__namespace_map__[cls.namespace] = cls

    def __new__(mcs, classname, bases, dict_):
        if classname == "BareEntityModel":
            return type.__new__(mcs, classname, bases, dict_)

        dict_ = dict(dict_)  # Make it writable

        __namespace__ = dict_.get('__namespace__', None)
        if isinstance(__namespace__, str):
            __namespace__ = uuid.uuid5(uuid.UUID(URN), __namespace__)
        assert isinstance(__namespace__, uuid)

        __mapper_args__ = dict_.get('__mapper_args__', {})
        __mapper_args__['polymorphic_identity'] = __namespace__
        # TODO: Error on already set?

        # pylint: disable=no-member
        dict_['__table__'] = MetadashEntity.__table__
        dict_['__namespace__'] = __namespace__
        dict_['__mapper_args__'] = __mapper_args__
        dict_['attribute_models'] = BareEntityModel.attribute_models[:]

        return super(BareEntityMeta, mcs).__new__(
            mcs, classname, (BareEntityModel, _Jsonable, MetadashEntity), dict_)


# pylint: disable=no-member
class BareEntityModel(metaclass=BareEntityMeta):
    """
    A entiry with no local storage/database,
    Used to reference to remote data.

    Need to provide a __namespace__ to identify it.
    __namespace__ should be either a UUID or a string, which will be
    hashed into a uuid5.
    """
    # Don't create any sqlalchemy things here
    # This class is just a skeleton
    # TODO: Raise error on create

    __alias__ = None

    attribute_models = []

    uuid = None  # Just a hint

    def identity(self):
        return '{}:{}(bare)'.format(self.__namespace__, self.uuid)

    def as_dict(self, detail=False):
        dict_ = super(BareEntityModel, self).as_dict()
        if detail:
            for model in self.attribute_models:
                dict_[model.backname] = _format_for_json(getattr(self, model.backname))
        return dict_