from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets
import os
import uuid
from PIL import Image
import shutil
from typing import Optional, List

from core.database import get_db, engine
from models.schemas import ProductCreate, ProductUpdate
from services.business import ProductService, CartService
from app.config import settings
import models.schemas as models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASICS Shoe Store", description="Premium ASICS Athletic Footwear")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.admin_username)
    correct_password = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with featured products"""
    product_service = ProductService(db)
    featured_products = product_service.get_featured_products(limit=8)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "featured_products": featured_products,
        "page_title": "ASICS - Premium Athletic Footwear"
    })

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request, category: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    """Product catalog page"""
    product_service = ProductService(db)
    
    if search:
        products = product_service.search_products(search)
    elif category:
        products = product_service.get_products_by_category(category)
    else:
        products = product_service.get_all_products()
    
    categories = product_service.get_categories()
    
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
        "categories": categories,
        "current_category": category,
        "search_query": search,
        "page_title": "Shop ASICS Shoes"
    })

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    """Product detail page"""
    product_service = ProductService(db)
    product = product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get related products
    related_products = product_service.get_products_by_category(product.category, limit=4, exclude_id=product_id)
    
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "related_products": related_products,
        "page_title": f"{product.name} - ASICS"
    })

@app.post("/cart/add/{product_id}")
async def add_to_cart(request: Request, product_id: int, quantity: int = Form(1), size: str = Form(...), db: Session = Depends(get_db)):
    """Add product to cart"""
    cart_service = CartService(db)
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        cart_service.add_to_cart(session_id, product_id, quantity, size)
        response = RedirectResponse(url="/cart", status_code=303)
        response.set_cookie("session_id", session_id, max_age=86400*7)  # 7 days
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cart", response_class=HTMLResponse)
async def view_cart(request: Request, db: Session = Depends(get_db)):
    """Shopping cart page"""
    session_id = request.cookies.get("session_id")
    cart_items = []
    total = 0
    
    if session_id:
        cart_service = CartService(db)
        cart_items = cart_service.get_cart_items(session_id)
        total = cart_service.get_cart_total(session_id)
    
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "cart_items": cart_items,
        "total": total,
        "page_title": "Shopping Cart - ASICS"
    })

@app.post("/cart/remove/{item_id}")
async def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    """Remove item from cart"""
    cart_service = CartService(db)
    cart_service.remove_from_cart(item_id)
    return RedirectResponse(url="/cart", status_code=303)

@app.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request, db: Session = Depends(get_db)):
    """Checkout page"""
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        return RedirectResponse(url="/cart", status_code=303)
    
    cart_service = CartService(db)
    cart_items = cart_service.get_cart_items(session_id)
    total = cart_service.get_cart_total(session_id)
    
    if not cart_items:
        return RedirectResponse(url="/cart", status_code=303)
    
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "cart_items": cart_items,
        "total": total,
        "page_title": "Checkout - ASICS"
    })

@app.post("/checkout/complete")
async def complete_checkout(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    postal_code: str = Form(...),
    db: Session = Depends(get_db)
):
    """Complete checkout process"""
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        return RedirectResponse(url="/cart", status_code=303)
    
    cart_service = CartService(db)
    
    try:
        order_id = cart_service.create_order(session_id, {
            "name": name,
            "email": email,
            "address": address,
            "city": city,
            "postal_code": postal_code
        })
        
        response = RedirectResponse(url=f"/order/success/{order_id}", status_code=303)
        response.delete_cookie("session_id")
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/order/success/{order_id}", response_class=HTMLResponse)
async def order_success(request: Request, order_id: int):
    """Order success page"""
    return templates.TemplateResponse("order_success.html", {
        "request": request,
        "order_id": order_id,
        "page_title": "Order Confirmed - ASICS"
    })

# Admin routes
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: str = Depends(verify_admin), db: Session = Depends(get_db)):
    """Admin dashboard"""
    product_service = ProductService(db)
    products = product_service.get_all_products()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "products": products,
        "page_title": "Admin Dashboard - ASICS"
    })

@app.get("/admin/products/add", response_class=HTMLResponse)
async def admin_add_product_form(request: Request, admin: str = Depends(verify_admin)):
    """Add product form"""
    return templates.TemplateResponse("admin/add_product.html", {
        "request": request,
        "page_title": "Add Product - Admin"
    })

@app.post("/admin/products/add")
async def admin_add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    sizes: str = Form(...),
    stock: int = Form(...),
    featured: bool = Form(False),
    image: UploadFile = File(...),
    admin: str = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Add new product"""
    # Save uploaded image
    image_filename = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(settings.upload_dir, image_filename)
    
    # Process and save image
    with Image.open(image.file) as img:
        img = img.convert("RGB")
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        img.save(image_path, "JPEG", quality=85)
    
    # Create product
    product_service = ProductService(db)
    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        sizes=sizes.split(","),
        stock=stock,
        featured=featured,
        image_url=f"/static/images/products/{image_filename}"
    )
    
    product_service.create_product(product_data)
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ASICS E-commerce Store"}