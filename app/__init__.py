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

app.config['VNPAY_TMN_CODE'] = '1FU6WO1F'
app.config['VNPAY_HASH_SECRET_KEY'] = 'P0062C5F3ROOTQ8JJU03FKXO4FFX7ENR'
app.config['VNPAY_PAYMENT_URL'] = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
app.config['VNPAY_RETURN_URL'] = 'http://localhost:5000/vnpay_return'