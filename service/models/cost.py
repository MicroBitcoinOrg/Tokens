from tortoise import fields
from .base import Base

class FeeAddress(Base):
    label = fields.CharField(max_length=64)
    height = fields.IntField()

    block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
        "models.Block", related_name="fee_addresses",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "service_fee_addresses"

class TokenCost(Base):
    value = fields.DecimalField(max_digits=28, decimal_places=8)
    category = fields.CharField(index=True, max_length=32)
    action = fields.CharField(index=True, max_length=32)
    height = fields.IntField()

    block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
        "models.Block", related_name="costs",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "service_costs"