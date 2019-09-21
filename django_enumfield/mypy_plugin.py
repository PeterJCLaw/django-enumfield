from typing import Callable, Optional

from mypy.mro import calculate_mro
from mypy.nodes import (
    Block,
    ClassDef,
    GDEF,
    MDEF,
    SymbolTable,
    SymbolTableNode,
    TypeInfo,
    Var,
)
from mypy.plugin import DynamicClassDefContext, Plugin
from mypy.types import Instance


def enum_function_hook(ctx: DynamicClassDefContext) -> None:
    """
    Given an enum construction like:

        FooEnum = Enum('FooEnum',
            FooItem(10, 'foo'),
        )

    We create a new type `FooEnum`, which extends from `Enum[FooItem]` and has
    an extra attribute `FOO`. This is roughly equivalent to the following code:

        class FooEnum(Enum[FooItem]):
            FOO = FooItem(10, 'foo')
    """
    # Work out the base -- build up `Enum[FooItem]`
    # TODO: should probably build a union if there's more than one type
    # (rather than erroring).
    item_typeinfo, = set(x.callee.node for x in ctx.call.args[1:])
    base_enum_typeinfo = ctx.call.callee.node

    item_type = Instance(item_typeinfo, [])
    enum_type = Instance(base_enum_typeinfo, [item_type])

    # At this point, `enum_type` is for the type `Enum[MyItem]`, which will
    # be the base class of the new type we're creating.

    # Define our new type
    class_def = ClassDef(ctx.name, Block([]))
    class_def.fullname = ctx.api.qualified_name(ctx.name)

    info = TypeInfo(SymbolTable(), class_def, ctx.api.cur_mod_id)
    info.bases = [enum_type]
    class_def.info = info
    calculate_mro(info)

    # Put the type into the local context
    new_type = Var(ctx.name, Instance(info, []))
    new_type.info = info
    new_type._fullname = ctx.api.qualified_name(ctx.name)

    ctx.api.add_symbol_table_node(
        ctx.name,
        SymbolTableNode(GDEF, new_type),
    )

    # Add the members of the enum as properties on it
    for arg in ctx.call.args[1:]:
        # Make the assumption that the signature for the item type is
        # unchanged from the base `Item` type.
        try:
            slug_index = arg.arg_names.index('slug')
        except ValueError:
            slug_index = 1
        slug = arg.args[slug_index].value

        attr_name = slug.upper()

        attr = Var(attr_name, Instance(item_typeinfo, []))
        attr.info = info
        attr._fullname = info.fullname() + '.' + attr_name
        info.names[attr_name] = SymbolTableNode(MDEF, attr)


class DjangoEnumFieldPlugin(Plugin):
    def get_dynamic_class_hook(
        self,
        fullname: str,
    ) -> Optional[Callable[[DynamicClassDefContext], None]]:
        if fullname == 'django_enumfield.enum.Enum':
            return enum_function_hook

        return None


def plugin(version: str) -> Plugin:
    return DjangoEnumFieldPlugin
