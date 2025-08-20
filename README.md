# 🛍️ Multi-Vendor E-Commerce Django REST API

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/) 
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django&logoColor=white)](https://www.djangoproject.com/) 
[![REST API](https://img.shields.io/badge/REST-API-blueviolet)](https://www.django-rest-framework.org/) 
[![JWT](https://img.shields.io/badge/JWT-Authentication-yellowgreen)](https://jwt.io/)

---

## 📌 Project Overview
Multi-Vendor E-Commerce Platform built with **Django REST Framework**.  
Supports multiple vendors, product management, and JWT authentication.
This API allows vendors to manage their products, customers to create wishlists and carts, and users to securely register and log in.
It provides a robust backend for an e-commerce application, enabling seamless order processing and checkout experiences.
This project is part of the Solvit Africa Training Center initiative, aimed at enhancing skills in web development and API design.

---

## ✨ Features
- Multi-vendor support  
- Product CRUD operations  
- Wishlist & Cart management  
- JWT authentication  
- Secure registration & login  
- Order processing & checkout  

---

## ⚡ Tech Stack
- **Backend:** Python, Django, Django REST Framework  
- **Authentication:** Simple JWT  
- **Database:** PostgreSQL / SQLite  
- **API Docs:** Swagger / DRF Spectacular  

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+  
- Django 4+  
- Virtualenv  
- PostgreSQL (optional)  

### Installation
```bash
git clone https://github.com/Solvit-Africa-Training-Center/e-commerce-team-Avatar
cd e-commerce-team-Avatar
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


```
### Environment Variables
Create a `.env` file in the root directory and add the following variables:
```env
SECRET_KEY=your_secret_key
DEBUG=True  
ALLOWED_HOSTS=localhost,
```


## 👥 Contributors

| Name | GitHub | Email |
|------|--------|-------|
| JEAN D Amour Niyokwizera | [@jeid12](https://github.com/jeid12) ![JEAN D Amour](https://github.com/jeid12.png?size=40) | niyokwizerajd123@gmail.com |
| Imanirahari Didier | [@didier_building](https://github.com/didier_building) ![Didier](https://github.com/didier_building.png?size=40) | didier53053@gmail.com |
| Masezerano Esther | [@esthersafina](https://github.com/esthersafina) ![Esther](https://github.com/esthersafina.png?size=40) | masezeranoesther20gmail.com |
