from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.schemas import Product, CartItem, Order, OrderItem, ProductCreate, ProductUpdate
from typing import List, Optional, Dict
import json

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_products(self) -> List[Product]:
        return self.db.query(Product).all()
    
    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_featured_products(self, limit: int = 8) -> List[Product]:
        return self.db.query(Product).filter(Product.featured == True).limit(limit).all()
    
    def get_products_by_category(self, category: str, limit: Optional[int] = None, exclude_id: Optional[int] = None) -> List[Product]:
        query = self.db.query(Product).filter(Product.category == category)
        if exclude_id:
            query = query.filter(Product.id != exclude_id)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def search_products(self, search_term: str) -> List[Product]:
        return self.db.query(Product).filter(
            or_(
                Product.name.contains(search_term),
                Product.description.contains(search_term),
                Product.category.contains(search_term)
            )
        ).all()
    
    def get_categories(self) -> List[str]:
        categories = self.db.query(Product.category).distinct().all()
        return [cat[0] for cat in categories]
    
    def create_product(self, product_data: ProductCreate) -> Product:
        # Convert sizes list to JSON string
        sizes_json = json.dumps(product_data.sizes)
        
        product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category=product_data.category,
            sizes=sizes_json,
            stock=product_data.stock,
            featured=product_data.featured,
            image_url=product_data.image_url
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        product = self.get_product(product_id)
        if not product:
            return None
        
        for field, value in product_data.dict(exclude_unset=True).items():
            if field == "sizes" and value:
                value = json.dumps(value)
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        product = self.get_product(product_id)
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        return True

class CartService:
    def __init__(self, db: Session):
        self.db = db
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int, size: str):
        # Check if item already exists in cart
        existing_item = self.db.query(CartItem).filter(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id,
            CartItem.size == size
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(
                session_id=session_id,
                product_id=product_id,
                quantity=quantity,
                size=size
            )
            self.db.add(cart_item)
        
        self.db.commit()
    
    def get_cart_items(self, session_id: str) -> List[Dict]:
        cart_items = self.db.query(CartItem).filter(CartItem.session_id == session_id).all()
        
        items_with_details = []
        for item in cart_items:
            product = item.product
            subtotal = product.price * item.quantity
            
            # Parse sizes from JSON
            try:
                sizes = json.loads(product.sizes) if product.sizes else []
            except:
                sizes = []
            
            items_with_details.append({
                "id": item.id,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image_url": product.image_url,
                    "sizes": sizes
                },
                "quantity": item.quantity,
                "size": item.size,
                "subtotal": subtotal
            })
        
        return items_with_details
    
    def get_cart_total(self, session_id: str) -> float:
        cart_items = self.get_cart_items(session_id)
        return sum(item["subtotal"] for item in cart_items)
    
    def remove_from_cart(self, item_id: int):
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
    
    def clear_cart(self, session_id: str):
        self.db.query(CartItem).filter(CartItem.session_id == session_id).delete()
        self.db.commit()
    
    def create_order(self, session_id: str, customer_data: Dict) -> int:
        cart_items = self.get_cart_items(session_id)
        if not cart_items:
            raise ValueError("Cart is empty")
        
        total_amount = self.get_cart_total(session_id)
        
        # Create order
        order = Order(
            customer_name=customer_data["name"],
            customer_email=customer_data["email"],
            shipping_address=f"{customer_data['address']}, {customer_data['city']}, {customer_data['postal_code']}",
            total_amount=total_amount
        )
        
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item["product"]["id"],
                quantity=cart_item["quantity"],
                size=cart_item["size"],
                price=cart_item["product"]["price"]
            )
            self.db.add(order_item)
        
        # Clear cart
        self.clear_cart(session_id)
        
        self.db.commit()
        return order.id