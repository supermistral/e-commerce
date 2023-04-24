from __future__ import annotations
from typing import Any, Optional

from sqlalchemy import (
    String, Text, ForeignKey, CheckConstraint, Dialect
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.types import TypeDecorator, String, TypeEngine

from .db.base import Base


class ImageType(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        return dialect.type_descriptor(String(255))


class Manufacturer(Base):
    __tablename__ = 'manufacturers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(Text, deferred=True)
    image: Mapped[Optional[ImageType]] = mapped_column(ImageType)

    products: Mapped[list[Product]] = relationship(back_populates='manufacturer')


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[Optional[ImageType]] = mapped_column(ImageType)
    # Adjacency list + nested set
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.id'))
    left: Mapped[int]
    right: Mapped[int]

    parent: Mapped[Optional[Category]] = relationship(back_populates='children')
    children: Mapped[list[Category]] = relationship(back_populates='parent')
    options: Mapped[list[ProductOption]] = relationship(back_populates='category')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, deferred=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey('manufacturers.id'))

    manufacturer: Mapped[Manufacturer] = relationship(back_populates='products')
    items: Mapped[list[ProductItem]] = relationship(back_populates='product')
    images: Mapped[list[ProductImage]] = relationship(back_populates='product')


class ProductImage(Base):
    __tablename__ = 'product_images'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    image: Mapped[ImageType] = mapped_column(ImageType)

    product: Mapped[Product] = relationship(back_populates='images')


class ProductItem(Base):
    __tablename__ = 'product_items'

    sku: Mapped[str] = mapped_column(String(12), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    price: Mapped[int]
    quantity: Mapped[int] = mapped_column()

    product: Mapped[Product] = relationship(back_populates='items')

    __table_args__ = (
        CheckConstraint(quantity >= 0, name='check_quantity_non_negative'),
    )


class ProductOption(Base):
    __tablename__ = 'product_options'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category: Mapped[Category] = relationship(back_populates='options')


class ProductOptionValue(Base):
    __tablename__ = 'product_option_values'

    id: Mapped[int] = mapped_column(primary_key=True)
    option_id: Mapped[int] = mapped_column(ForeignKey('product_options.id'))
    value: Mapped[str] = mapped_column(String(30))

    option: Mapped[ProductOption] = relationship(back_populates='option_values')


class ProductItemOptionValue(Base):
    __tablename__ = 'product_item_option_values'

    sku: Mapped[str] = mapped_column(
        ForeignKey('product_items.sku'),
        primary_key=True,
    )
    option_id: Mapped[int] = mapped_column(
        ForeignKey('product_option_values.option_id'),
        primary_key=True,
    )
    value_id: Mapped[int] = mapped_column(ForeignKey('product_option_values.id'))

    option: Mapped[ProductOption] = relationship(back_populates='item_option_values')
    option_value: Mapped[ProductOptionValue] = relationship(back_populates='item_option_values')
