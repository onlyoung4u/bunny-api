from enum import Enum

from tortoise import fields

from .base import BaseModel


class BunnyUser(BaseModel):
    username = fields.CharField(max_length=64, unique=True)
    nickname = fields.CharField(max_length=64)
    password = fields.CharField(max_length=255)
    last_login_time = fields.IntField(default=0)
    last_login_ip = fields.CharField(max_length=15, default='')
    is_active = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False, index=True)

    created_roles: fields.ReverseRelation['BunnyRole']

    roles: fields.ManyToManyRelation['BunnyRole'] = fields.ManyToManyField(
        'models.BunnyRole',
        forward_key='user_id',
        backward_key='role_id',
        related_name='users',
        through='bunny_user_roles',
    )

    class Meta:
        table = 'bunny_users'

    class PydanticMeta:
        exclude = ['password']


class BunnyRole(BaseModel):
    name = fields.CharField(max_length=64, unique=True)

    creator = fields.ForeignKeyField(
        'models.BunnyUser', related_name='created_roles', db_constraint=False
    )

    permissions: fields.ReverseRelation['BunnyRolePermission']

    class Meta:
        table = 'bunny_roles'


class BunnyRolePermission(BaseModel):
    permission = fields.CharField(max_length=64)

    role = fields.ForeignKeyField(
        'models.BunnyRole', related_name='permissions', db_constraint=False
    )

    class Meta:
        table = 'bunny_role_permissions'
        unique_together = ('role_id', 'permission')


class BunnyUserRole(BaseModel):
    user_id = fields.IntField()
    role_id = fields.IntField()

    class Meta:
        table = 'bunny_user_roles'
        unique_together = ('user_id', 'role_id')


class BunnyMenu(BaseModel):
    parent_id = fields.IntField()
    title = fields.CharField(max_length=64)
    path = fields.CharField(max_length=64)
    permission = fields.CharField(max_length=64, unique=True)
    icon = fields.CharField(max_length=64, default='')
    link = fields.CharField(max_length=255, default='')
    sort = fields.SmallIntField(default=0)
    hidden = fields.BooleanField(default=False)
    is_system = fields.BooleanField(default=False)

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
    nickname = fields.CharField(max_length=64)
    path = fields.CharField(max_length=255)
    route = fields.CharField(max_length=64)
    method = fields.CharField(max_length=10)
    ip = fields.CharField(max_length=15)
    content = fields.JSONField()
    is_success = fields.BooleanField()

    class Meta:
        table = 'bunny_operation_logs'
