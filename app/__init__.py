from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.secret_key = 'HVQG93RHG9843GRJNVIPQV93GH9Q34G09HFFPI2'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/saleticketdb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config( 
  cloud_name = "truongduchoang", 
  api_key = "248579782829654", 
  api_secret = "sxkpzv4-ePJKtM6PFD6ZUi6FHxE"
)