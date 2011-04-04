# -*- coding: utf-8 -*-
# sammy.models

from google.appengine.ext import db

# The domain name of this application.  The application hosts multiple
# repositories, each at a subdomain of this domain.
HOME_DOMAIN = 'k2onepiece.appspot.com'


# ==== PFIF record IDs =====================================================

def is_original(subdomain, record_id):
    """Returns True if this is a record_id for an original record in the given
    subdomain (a record originally created in this subdomain's repository)."""
    try:
        domain, local_id = record_id.split('/', 1)
        return domain == subdomain + '.' + HOME_DOMAIN
    except ValueError:
        raise ValueError('%r is not a valid record_id' % record_id)

def is_clone(subdomain, record_id):
    """Returns True if this is a record_id for a clone record (a record created
    in another repository and copied into this one)."""
    return not is_original(subdomain, record_id)

def filter_by_prefix(query, key_name_prefix):
    """Filters a query for key_names that have the given prefix.  If root_kind
    is specified, filters the query for children of any entities that are of
    that kind with the given prefix; otherwise, the results are assumed to be
    top-level entities of the kind being queried."""
    root_kind = query._model_class.__name__
    min_key = db.Key.from_path(root_kind, key_name_prefix)
    max_key = db.Key.from_path(root_kind, key_name_prefix + u'\uffff')
    return query.filter('__key__ >=', min_key).filter('__key__ <=', max_key)

def get_properties_as_dict(db_obj):
    """Returns a dictionary containing all (dynamic)* properties of db_obj."""
    properties = dict((k, v.__get__(db_obj, db_obj.__class__)) for
                      k, v in db_obj.properties().iteritems() if
                      v.__get__(db_obj, db_obj.__class__))
    dynamic_properties = dict((prop, getattr(db_obj, prop)) for
                              prop in db_obj.dynamic_properties())
    properties.update(dynamic_properties)
    return properties

def clone_to_new_type(origin, dest_class, **kwargs):
    """Clones the given entity to a new entity of the type "dest_class".
    Optionally, pass in values to kwargs to update values during cloning."""
    vals = get_properties_as_dict(origin)
    vals.update(**kwargs)
    if hasattr(origin, 'record_id'):
        vals.update(record_id=origin.record_id)
    return dest_class(key_name=origin.key().name(), **vals)

# ==== Model classes =======================================================

# Every Person or Note entity belongs to a specific subdomain.  To partition
# the datastore, key names consist of the subdomain, a colon, and then the
# record ID.  Each subdomain appears to be a separate instance of the app
# with its own respository.

# Note that the repository subdomain doesn't necessarily have to match the
# domain in the record ID!  For example, a person record created at
# foo.person-finder.appspot.com would have a key name such as:
#
#     foo:foo.person-finder.appspot.com/person.234
#
# This record would be searchable only at foo.person-finder.appspot.com --
# each repository is independent.  Copying it to bar.person-finder.appspot.com
# would produce a clone record with the key name:
#
#     bar:foo.person-finder.appspot.com/person.234
#
# That is, the clone has the same record ID but a different subdomain.

class Subdomain(db.Model):
    """A separate grouping of Person and Note records.  This is a top-level
    entity, with no parent, whose existence just indicates the existence of
    a subdomain.  Key name: unique subdomain name.  In the UI, each subdomain
    appears to be an independent instance of the application."""
    # No properties for now; only the key_name is significant.

    @staticmethod
    def list():
        return [subdomain.key().name() for subdomain in Subdomain.all()]

class Base(db.Model):
    """Base class providing methods common to both Person and Note entities,
    whose key names are partitioned using the subdomain as a prefix."""

    # Even though the subdomain is part of the key_name, it is also stored
    # redundantly as a separate property so it can be indexed and queried upon.
    subdomain = db.StringProperty(required=True)

    @classmethod
    def all(cls, keys_only=False):
        """Returns a query for all records of this kind; by default this
        filters out the records marked as expired.

        Args:
          keys_only - If true, return only the keys.
          filter_expired - If true, omit records with is_expired == True.
        Returns:
          query - A Query object for the results.
        """
        query = super(Base, cls).all(keys_only=keys_only)
        return query

    @classmethod
    def all_in_subdomain(cls, subdomain):
        """Gets a query for all entities in a given subdomain's repository."""
        return cls.all().filter('subdomain =', subdomain)

    def get_record_id(self):
        """Returns the record ID of this record."""
        subdomain, record_id = self.key().name().split(':', 1)
        return record_id
    record_id = property(get_record_id)

    @classmethod
    def get(cls, subdomain, record_id):
        """Gets the entity with the given record_id in a given repository."""
        record = cls.get_by_key_name(subdomain + ':' + record_id)
        if record:
            return record

    @classmethod
    def create_original(cls, subdomain, **kwargs):
        """Creates a new original entity with the given field values."""
        record_id = '%s.%s/%s.%d' % (
            subdomain, HOME_DOMAIN, cls.__name__.lower(), UniqueId.create_id())
        key_name = subdomain + ':' + record_id
        return cls(key_name=key_name, subdomain=subdomain, **kwargs)

    @classmethod
    def create_clone(cls, subdomain, record_id, **kwargs):
        """Creates a new clone entity with the given field values."""
        assert is_clone(subdomain, record_id)
        key_name = subdomain + ':' + record_id
        return cls(key_name=key_name, subdomain=subdomain, **kwargs)

    @classmethod
    def create_original_with_record_id(cls, subdomain, record_id, **kwargs):
        """Creates an original entity with the given record_id and field
        values, overwriting any existing entity with the same record_id.
        This should be rarely used in practice (e.g. for an administrative
        import into a home repository), hence the long method name."""
        key_name = subdomain + ':' + record_id
        return cls(key_name=key_name, subdomain=subdomain, **kwargs)

class StaticContent(Base):
    body = db.BlobProperty()
    content_type = db.StringProperty(required=True)
    status = db.IntegerProperty(required=True, default=200)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)

class UniqueId(db.Model):
    """This entity is used just to generate unique numeric IDs."""
    @staticmethod
    def create_id():
        """Gets an integer ID that is guaranteed to be different from any ID
        previously returned by this static method."""
        unique_id = UniqueId()
        unique_id.put()
        return unique_id.key().id()
