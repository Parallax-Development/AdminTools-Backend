from abc import ABC, abstractmethod
from contextlib import contextmanager

from bson import ObjectId
from pymongo import ReturnDocument
from django.db import transaction
from django.utils import timezone

from core.db.mongo import get_mongo_database


class BaseDAO(ABC):
    @abstractmethod
    def create(self, data):
        raise NotImplementedError

    @abstractmethod
    def get(self, **filters):
        raise NotImplementedError

    @abstractmethod
    def list(self, filters=None, order_by=None, limit=None):
        raise NotImplementedError

    @abstractmethod
    def update(self, identifier, data):
        raise NotImplementedError

    @abstractmethod
    def delete(self, identifier):
        raise NotImplementedError

    @contextmanager
    def transaction(self):
        yield


class DjangoDAO(BaseDAO):
    def __init__(self, model, mapper):
        self.model = model
        self.mapper = mapper

    def create(self, data):
        normalized = self._normalize_data(data)
        instance = self.model.objects.create(**normalized)
        return self.mapper(instance)

    def get(self, **filters):
        instance = self.model.objects.filter(**filters).first()
        return self.mapper(instance) if instance else None

    def list(self, filters=None, order_by=None, limit=None):
        queryset = self.model.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        if order_by:
            queryset = queryset.order_by(order_by)
        if limit:
            queryset = queryset[:limit]
        return [self.mapper(item) for item in queryset]

    def update(self, identifier, data):
        instance = self.model.objects.filter(id=identifier).first()
        if not instance:
            return None
        normalized = self._normalize_data(data)
        for key, value in normalized.items():
            setattr(instance, key, value)
        instance.save()
        return self.mapper(instance)

    def delete(self, identifier):
        return self.model.objects.filter(id=identifier).delete()[0] > 0

    @contextmanager
    def transaction(self):
        with transaction.atomic():
            yield

    def _normalize_data(self, data):
        normalized = {}
        for key, value in data.items():
            if key.endswith("_id") or value is None:
                normalized[key] = value
                continue
            try:
                field = self.model._meta.get_field(key)
            except Exception:
                normalized[key] = value
                continue
            if field.is_relation and not isinstance(value, field.related_model):
                normalized[f"{key}_id"] = value
            else:
                normalized[key] = value
        return normalized


class MongoDAO(BaseDAO):
    def __init__(self, collection_name, mapper=None):
        self.collection = get_mongo_database()[collection_name]
        self.mapper = mapper or self._default_mapper

    def create(self, data):
        payload = data.copy()
        payload.setdefault("created_at", timezone.now())
        result = self.collection.insert_one(payload)
        payload["_id"] = result.inserted_id
        return self.mapper(payload)

    def get(self, **filters):
        normalized = self._normalize_filters(filters)
        item = self.collection.find_one(normalized)
        return self.mapper(item) if item else None

    def list(self, filters=None, order_by=None, limit=None):
        normalized = self._normalize_filters(filters or {})
        cursor = self.collection.find(normalized)
        if order_by:
            direction = -1 if order_by.startswith("-") else 1
            field = order_by.lstrip("-")
            if field == "id":
                field = "_id"
            cursor = cursor.sort(field, direction)
        if limit:
            cursor = cursor.limit(limit)
        return [self.mapper(item) for item in cursor]

    def update(self, identifier, data):
        mongo_id = self._normalize_id(identifier)
        data["updated_at"] = timezone.now()
        result = self.collection.find_one_and_update(
            {"_id": mongo_id}, {"$set": data}, return_document=ReturnDocument.AFTER
        )
        return self.mapper(result) if result else None

    def delete(self, identifier):
        mongo_id = self._normalize_id(identifier)
        result = self.collection.delete_one({"_id": mongo_id})
        return result.deleted_count > 0

    @contextmanager
    def transaction(self):
        client = self.collection.database.client
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    yield
        except Exception:
            yield

    def _normalize_id(self, identifier):
        if isinstance(identifier, ObjectId):
            return identifier
        try:
            return ObjectId(str(identifier))
        except Exception:
            return identifier

    def _normalize_filters(self, filters):
        normalized = {}
        for key, value in filters.items():
            if key == "id":
                normalized["_id"] = self._normalize_id(value)
                continue
            if key.endswith("__isnull"):
                field = key.replace("__isnull", "")
                if value:
                    normalized[field] = None
                else:
                    normalized[field] = {"$ne": None}
                continue
            if key.endswith("__in") and isinstance(value, (list, tuple)):
                field = key.replace("__in", "")
                normalized[field] = {"$in": value}
                continue
            else:
                normalized[key] = value
        return normalized

    def _default_mapper(self, item):
        if not item:
            return None
        data = item.copy()
        data["id"] = str(data.pop("_id"))
        return data
