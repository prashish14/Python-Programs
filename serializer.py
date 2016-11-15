import warnings

from django.db import models
from django.utils import six
from django.utils.deprecation import RemovedInDjango19Warning


class SerializerDoesNotExist(KeyError):
    
    pass


class SerializationError(Exception):
    
    pass


class DeserializationError(Exception):
   
    pass


class Serializer(object):
   
    internal_use_only = False

    def serialize(self, queryset, **options):
      
        self.options = options

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)
        if self.use_natural_keys:
            warnings.warn("``use_natural_keys`` is deprecated; use ``use_natural_foreign_keys`` instead.",
                RemovedInDjango19Warning)
        self.use_natural_foreign_keys = options.pop('use_natural_foreign_keys', False) or self.use_natural_keys
        self.use_natural_primary_keys = options.pop('use_natural_primary_keys', False)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            for field in concrete_model._meta.local_fields:
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

    def start_serialization(self):
       
        raise NotImplementedError('subclasses of Serializer must provide a start_serialization() method')

    def end_serialization(self):
        
        pass

    def start_object(self, obj):
       
        raise NotImplementedError('subclasses of Serializer must provide a start_object() method')

    def end_object(self, obj):
       
        pass

    def handle_field(self, obj, field):
     
        raise NotImplementedError('subclasses of Serializer must provide an handle_field() method')

    def handle_fk_field(self, obj, field):
        
        raise NotImplementedError('subclasses of Serializer must provide an handle_fk_field() method')

    def handle_m2m_field(self, obj, field):
      
        raise NotImplementedError('subclasses of Serializer must provide an handle_m2m_field() method')

    def getvalue(self):
      
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()


class Deserializer(six.Iterator):
   
    def __init__(self, stream_or_string, **options):
     
        self.options = options
        if isinstance(stream_or_string, six.string_types):
            self.stream = six.StringIO(stream_or_string)
        else:
            self.stream = stream_or_string

    def __iter__(self):
        return self

    def __next__(self):
        

class DeserializedObject(object):
    
    def __init__(self, obj, m2m_data=None):
        self.object = obj
        self.m2m_data = m2m_data

    def __repr__(self):
        return "<DeserializedObject: %s.%s(pk=%s)>" % (
            self.object._meta.app_label, self.object._meta.object_name, self.object.pk)

    def
        models.Model.save_base(self.object, using=using, raw=True)
        if self.m2m_data and save_m2m:
            for accessor_name, object_list in self.m2m_data.items():
                setattr(self.object, accessor_name, object_list)

        self.m2m_data = None


def build_instance(Model, data, db):
 
    obj = Model(**data)
    if (obj.pk is None and hasattr(Model, 'natural_key') and
            hasattr(Model._default_manager, 'get_by_natural_key')):
        natural_key = obj.natural_key()
        try:
            obj.pk = Model._default_manager.db_manager(db).get_by_natural_key(*natural_key).pk
        except Model.DoesNotExist:
            pass
    return obj
