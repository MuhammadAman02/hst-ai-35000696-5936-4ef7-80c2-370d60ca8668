# ASICS E-commerce Store

A professional e-commerce platform for selling ASICS athletic footwear, built with FastAPI and modern web technologies.

## Features

### 🛍️ Customer Features
- **Product Catalog**: Browse ASICS shoes by category (Running, Training, Lifestyle, Tennis)
- **Product Search**: Find shoes by name, description, or category
- **Product Details**: Detailed product pages with size selection and high-quality images
- **Shopping Cart**: Add products to cart with size and quantity selection
- **Checkout Process**: Complete order placement with shipping information
- **Responsive Design**: Mobile-first design that works on all devices

### 👨‍💼 Admin Features
- **Product Management**: Add, view, and manage product inventory
- **Image Upload**: Upload and process product images automatically
- **Inventory Tracking**: Monitor stock levels and featured products
- **Dashboard**: Overview of products, stock status, and key metrics

### 🔧 Technical Features
- **FastAPI Backend**: High-performance async API with automatic documentation
- **SQLAlchemy ORM**: Robust database management with relationships
- **Jinja2 Templates**: Server-side rendering for SEO and performance
- **Image Processing**: Automatic image optimization and thumbnail generation
- **Session Management**: Persistent shopping cart across browser sessions
- **Security**: Input validation, CORS protection, and secure headers

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd asics-store
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Run the application**:
```bash
python main.py
```

4. **Access the store**:
- **Store**: http://localhost:8000
- **Admin**: http://localhost:8000/admin (admin/admin123)
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
asics-store/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── dockerfile             # Container configuration
├── fly.toml               # Deployment configuration
├── .env                   # Environment variables
├── app/
│   ├── main.py            # FastAPI application and routes
│   └── config.py          # Application configuration
├── core/
│   └── database.py        # Database connection and session management
├── models/
│   └── schemas.py         # SQLAlchemy and Pydantic models
├── services/
│   └── business.py        # Business logic and data services
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with navigation
│   ├── home.html          # Homepage with featured products
│   ├── products.html      # Product catalog and search
│   ├── product_detail.html # Individual product pages
│   ├── cart.html          # Shopping cart
│   ├── checkout.html      # Checkout process
│   ├── order_success.html # Order confirmation
│   └── admin/             # Admin interface templates
└── static/                # Static assets (CSS, JS, images)
```

## Database Schema

### Products
- Product information (name, description, price, category)
- Inventory management (stock, sizes)
- Image URLs and featured status

### Cart Items
- Session-based shopping cart
- Product associations with size and quantity

### Orders
- Customer information and shipping details
- Order items with pricing snapshot

## API Endpoints

### Public Routes
- `GET /` - Homepage with featured products
- `GET /products` - Product catalog with filtering and search
- `GET /product/{id}` - Product detail page
- `POST /cart/add/{product_id}` - Add product to cart
- `GET /cart` - View shopping cart
- `GET /checkout` - Checkout page
- `POST /checkout/complete` - Process order

### Admin Routes (Authentication Required)
- `GET /admin` - Admin dashboard
- `GET /admin/products/add` - Add product form
- `POST /admin/products/add` - Create new product

### Utility Routes
- `GET /health` - Health check endpoint

## Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./asics_store.db
SECRET_KEY=your-secret-key-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
DEBUG=True
UPLOAD_DIR=static/images/products
```

### Database Configuration
- SQLite for development (included)
- PostgreSQL support for production
- Automatic table creation on startup

## Deployment

### Docker Deployment
```bash
docker build -t asics-store .
docker run -p 8000:8000 asics-store
```

### Fly.io Deployment
```bash
fly deploy
```

### Production Considerations
- Change default admin credentials
- Use PostgreSQL for production database
- Configure proper secret key
- Set up SSL/TLS certificates
- Configure CDN for static assets

## Sample Data

The application includes sample ASICS products across categories:
- **Running**: Gel-Kayano, Gel-Nimbus series
- **Training**: Gel-Quantum, Cross-training shoes
- **Lifestyle**: Tiger series, casual sneakers
- **Tennis**: Court-specific performance shoes

## Security Features

- **Input Validation**: Pydantic models validate all input data
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Jinja2 template auto-escaping
- **CORS Configuration**: Proper cross-origin request handling
- **Session Security**: Secure cookie configuration
- **File Upload Security**: Image validation and processing

## Performance Optimizations

- **Async Operations**: FastAPI async support for database operations
- **Image Optimization**: Automatic image resizing and compression
- **Database Indexing**: Optimized queries for product search
- **Static Asset Caching**: Efficient static file serving
- **Lazy Loading**: Efficient data loading patterns

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health`
- Examine application logs for debugging

---

**Built with FastAPI, SQLAlchemy, and modern web technologies for a professional e-commerce experience.**