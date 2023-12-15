import datetime

from mongoengine import Document, ObjectIdField, DateTimeField, BooleanField, queryset_manager

from .mixin_document import DocumentMixin


class BaseBusinessDocument(Document, DocumentMixin):
    """
    业务数据的基类
    """
    creator_id = ObjectIdField()
    create_time = DateTimeField(default=datetime.datetime.utcnow())
    updator_id = ObjectIdField()
    update_time = DateTimeField(default=datetime.datetime.utcnow())
    is_deleted = BooleanField()
    delete_time = DateTimeField()

    meta = {'abstract': True}

    @queryset_manager
    def objects(doc_cls, queryset):
        """过滤已经逻辑删除的数据"""
        return queryset.filter(is_deleted__ne=True)

    @queryset_manager
    def ori_objects(doc_cls, queryset):
        """原始"""
        return queryset

    def set_deleted(self, updator_id=None):
        self.is_deleted = True
        self.delete_time = datetime.datetime.utcnow()
        if updator_id:
            self.updator_id = updator_id
        self.save(validate=False)
