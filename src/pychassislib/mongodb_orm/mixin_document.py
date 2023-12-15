from mongoengine import ReferenceField, ListField, EmbeddedDocumentField


def get_field(cls, key):
    if '.' not in key:
        field = cls._fields[key]
        return field
    attr_key, new_key = key.split('.', 1)
    v = cls._fields.get(attr_key)
    if hasattr(v, 'document_type'):
        return get_field(v.document_type, new_key)
    else:
        return get_field(v.field.document_type, new_key)


class DocumentMixin:

    def set_cached_property(self, k, v):
        """
        设置缓存，然后利用如下方式获取缓存数据：
        @cached_property
        def k(self):
            return v
        :param k:
        :param v:
        :return:
        """
        self.__dict__[k] = v

    def clear_cached_property(self, k):
        """
            清除对应的缓存数据
        :param k:
        :param v:
        :return:
        """
        if k in self.__dict__:
            del self.__dict__[k]

    def has_cached_property(self, k):
        return k in self.__dict__

    # ----------------------- reference fields 相关处理 -----------------------
    # LazyReferenceField 必须先fetch后使用,不符合需要的处理方式
    # fill_refer 在不改变 ReferenceField 的处理方式的前提下，减少了查询量
    # fill_refer 由对象调用,将 refer_cls 作为参数
    # fill_qs_refer 由 refer_cls 调用，将 query_set 转变的 list 作为参数
    def fill_refer(self, refer_cls, source=None, fields_dic=None):
        if fields_dic is None:
            ref_fields = self.__class__.get_reference_fields(refer_cls)
            fields_dic = {f: self.__class__._fields[f] for f in ref_fields if '.' not in f}
        else:
            ref_fields = list(fields_dic.keys())
        if source is None:
            source = self.get_all_ref_obj_dict(refer_cls, ref_fields)
        for field_key, field in fields_dic.items():
            if '.' not in field_key:
                if isinstance(field, ListField) and isinstance(field.field, ReferenceField) and \
                        field_key in self._data:
                    self._data[field_key] = [source[dbref.id] for dbref in self._data[field_key]]
                elif self._data.get(field_key):
                    self._data[field_key] = source[self._data[field_key].id]
        suffix_dic = {}
        for field_key in ref_fields:
            if '.' in field_key:
                attr, suffix = field_key.split('.', 1)
                if attr not in suffix_dic:
                    suffix_dic[attr] = [suffix]
                else:
                    suffix_dic[attr].append(suffix)
        for attr, suffix in suffix_dic.items():
            if attr in self._data:
                if isinstance(self._data[attr], list):
                    for x in self._data[attr]:
                        x.fill_refer(refer_cls, source)
                else:
                    self._data[attr].fill_refer(refer_cls, source)

    @classmethod
    def fill_qs_refer(cls, qs_list, refer_cls, source=None) -> list:
        """
        :param source:
        :return:
        """
        if not isinstance(qs_list, list):
            raise Exception('只接受数组型参数，QuerySet请自行转化为数组')
        ref_fields = cls.get_reference_fields(refer_cls)
        fields_dic = cls.get_reference_fields_dic(refer_cls)
        if source is None:
            ids = set()
            for d in qs_list:
                for i in d.get_all_ref_ids(ref_fields):
                    ids.add(i)
            source = {i.id: i for i in refer_cls.ori_objects(id__in=ids)}
        for d in qs_list:
            d.fill_refer(refer_cls, source, fields_dic)

    @classmethod
    def get_reference_fields(cls, target_cls=None):
        """
            target_cls = None -> {'key':cls}
            target_cls -> ['key']
        :param target_cls:
        :return:
        """
        key = '__reference_fields_%s' % target_cls.__name__ if target_cls else '__reference_fields_all'
        if hasattr(cls, key):
            return getattr(cls, key)
        res = []
        for f, v in cls._fields.items():
            if (isinstance(v, ReferenceField) and v.document_type is target_cls) or \
                    (isinstance(v, ListField) and isinstance(v.field,
                                                             ReferenceField) and v.field.document_type is target_cls):
                res.append(f)
            elif isinstance(v, EmbeddedDocumentField):
                if hasattr(v.document_type, 'get_reference_fields'):
                    ref = v.document_type.get_reference_fields(target_cls)
                    if ref:
                        for _i in ref:
                            res.append('%s.%s' % (f, _i))
            elif isinstance(v, ListField) and isinstance(v.field, EmbeddedDocumentField):
                if hasattr(v.field.document_type, 'get_reference_fields'):
                    ref = v.field.document_type.get_reference_fields(target_cls)
                    if ref:
                        for _i in ref:
                            res.append('%s.%s' % (f, _i))
        setattr(cls, key, res)
        return res

    @classmethod
    def get_reference_fields_dic(cls, target_cls=None):
        """
            target_cls = None -> {'key':cls}
            target_cls -> ['key']
        :param target_cls:
        :return:
        """
        fields = cls.get_reference_fields(target_cls)
        return {f: get_field(cls, f) for f in fields}

    def get_all_ref_ids(self, fields):
        ids = []
        suffix_dic = {}
        for field_key in fields:
            if '.' not in field_key:
                dbref = self._data[field_key] if field_key in self._data else None
                if dbref:
                    if isinstance(dbref, list):
                        ids.extend([i.id for i in dbref])
                    else:
                        ids.append(dbref.id)
            else:
                attr, suffix = field_key.split('.', 1)
                if attr not in suffix_dic:
                    suffix_dic[attr] = [suffix]
                else:
                    suffix_dic[attr].append(suffix)
        for attr, suffix in suffix_dic.items():
            if attr in self._data:
                if isinstance(self._data[attr], list):
                    for x in self._data[attr]:
                        ids.extend(x.get_all_ref_ids(suffix))
                else:
                    ids.extend(self._data[attr].get_all_ref_ids(suffix))
        return ids

    def get_all_ref_obj_dict(self, refer_cls, ref_fields):
        ids = self.get_all_ref_ids(ref_fields)
        res = refer_cls.ori_objects(id__in=ids)
        return {i.id: i for i in res}

    @classmethod
    def fill_qs_refer_all(cls, qs):
        fields = cls.get_reference_fields()
        for field in fields:
            cls.fill_qs_refer(qs, field.document_type)
        return qs

    @classmethod
    def fill_qs_props(cls, qs_list, props, sources=None) -> list:
        """
        :param props: {'<prop_property>': Model, '<prop_property>': [Model, '<prop>']}
        :param source:
        :return:
        """
        if not isinstance(qs_list, list):
            raise Exception('只接受数组型参数，QuerySet请自行转化为数组')
        for prop_property, model in props.items():
            if type(model) in (list, tuple):
                prop = model[1]
                model = model[0]
            else:
                prop = None
            cls.fill_qs_prop(qs_list, prop, model, prop_property, sources.get(prop, {}) if sources else None)
        return qs_list

    @classmethod
    def fill_qs_prop(cls, qs_list, prop, model, prop_property=None, source=None):
        """
        :param qs_list:
        :param prop: 如 creator_id，
        :param model:
        :param prop_property:
        :param source: 如果提供了source 参数，则 source 必须涵盖所有记录，不在 source 中的会设置为 None
        :return:
        """
        if not isinstance(qs_list, list):
            raise Exception('只接受数组型参数，QuerySet 请自行转化为数组')
        if '__' in prop:
            raise Exception('暂不支持复杂对象内 cached_property 的设置，建议在复杂对象内部直接使用 ReferenceField')
        if prop is None:
            if '_id' in prop:
                prop = prop_property.replace('_id', '')
            else:
                prop = prop_property

        def get_field_attr(obj, prop):
            return getattr(obj, prop)

        if source is None:
            ids = set()
            for d in qs_list:
                v = get_field_attr(d, prop)
                ids.add(v)
            source = {i.id: i for i in model.ori_objects(id__in=ids)}
        for d in qs_list:
            d.set_cached_property(prop_property, source.get(get_field_attr(d, prop), None))
        return qs_list