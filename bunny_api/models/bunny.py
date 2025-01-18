from enum import Enum

from tortoise import fields

from .base import BaseModel, BaseModelWithoutTimestamp


class BunnyUser(BaseModel):
    username = fields.CharField(max_length=64, unique=True)
    nickname = fields.CharField(max_length=64)
    password = fields.CharField(max_length=255)
    last_login_time = fields.IntField(default=0)
    last_login_ip = fields.CharField(max_length=15, default='')
    is_active = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False, index=True)

    roles: fields.ManyToManyRelation['BunnyRole'] = fields.ManyToManyField(
        'models.BunnyRole', related_name='users', through='bunny_user_roles'
    )

    class Meta:
        table = 'bunny_users'


class BunnyRole(BaseModel):
    name = fields.CharField(max_length=64, unique=True)
    permissions = fields.JSONField()
    creator_id = fields.IntField()

    class Meta:
        table = 'bunny_roles'


class BunnyUserRole(BaseModelWithoutTimestamp):
    user = fields.ForeignKeyField('models.BunnyUser', related_name='user_roles', db_constraint=False)
    role = fields.ForeignKeyField('models.BunnyRole', related_name='user_roles', db_constraint=False)

    class Meta:
        table = 'bunny_user_roles'


class BunnyMenu(BaseModel):
    parent_id = fields.IntField()
    title = fields.CharField(max_length=64)
    path = fields.CharField(max_length=64)
    permission = fields.CharField(max_length=64, unique=True)
    icon = fields.CharField(max_length=64, default='')
    link = fields.CharField(max_length=255, default='')
    hidden = fields.BooleanField(default=False)
    sort = fields.SmallIntField(default=0)

    class Meta:
        table = 'bunny_menus'


class BunnyConfigGroup(str, Enum):
    SYSTEM = 'system'  # 系统配置
    PAYMENT = 'payment'  # 支付配置
    OTHER = 'other'  # 其他配置

    LABELS = {
        SYSTEM: '系统配置',
        PAYMENT: '支付配置',
        OTHER: '其他配置',
    }


class BunnyConfigType(str, Enum):
    STRING = 'string'  # 字符串
    NUMBER = 'number'  # 数字
    BOOLEAN = 'boolean'  # 开关
    SELECT = 'select'  # 下拉框
    RADIO = 'radio'  # 单选框
    CHECKBOX = 'checkbox'  # 复选框
    TEXT = 'text'  # 文本
    JSON = 'json'  # JSON

    LABELS = {
        STRING: '字符串',
        NUMBER: '数字',
        BOOLEAN: '开关',
        SELECT: '下拉框',
        RADIO: '单选框',
        CHECKBOX: '复选框',
        TEXT: '文本',
        JSON: 'JSON',
    }


class BunnyConfig(BaseModel):
    group = fields.CharEnumField(BunnyConfigGroup)
    type = fields.CharEnumField(BunnyConfigType)
    key = fields.CharField(max_length=64, unique=True)
    name = fields.CharField(max_length=64)
    value = fields.TextField()
    options = fields.JSONField()
    remark = fields.CharField(max_length=255, default='')
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = 'bunny_configs'


class BunnyOperationLog(BaseModel):
    user_id = fields.IntField()
    username = fields.CharField(max_length=64)
    path = fields.CharField(max_length=255)
    method = fields.CharField(max_length=10)
    ip = fields.CharField(max_length=15)
    content = fields.JSONField()

    class Meta:
        table = 'bunny_operation_logs'
