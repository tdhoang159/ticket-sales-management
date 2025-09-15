from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from app import app, db
from enum import Enum as ClassEnum
from flask_login import UserMixin 

class UserRole(ClassEnum):
    ADMIN = 1
    USER = 2

class Gender(ClassEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), default=Gender.MALE, nullable=True)
    dob = Column(Date, nullable=True)  # Date: yyyy-mm-dd
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=True, 
                    default="https://res.cloudinary.com/truongduchoang/image/upload/v1757070658/default_user_fy8beq.jpg")
    user_role = Column(Enum(UserRole), default=UserRole.USER)



class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False, unique=True)
    events = relationship('Event', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Event(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    description = Column(String(2000), nullable=True)
    datetime = Column(DateTime, nullable=False)
    organizer = Column(String(500), nullable=False)
    vip_price = Column(Float, nullable=True)
    normal_price = Column(Float, nullable=False)
    vip_quantity = Column(Integer, nullable=True)
    normal_quantity = Column(Integer, nullable=False)
    address_detail = Column(String(500), nullable=True)
    province = Column(String(50), nullable=False)
    banner = Column(String(1000), nullable=True)
    active = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)

    def __str__(self):
        return self.name

if __name__ == "__main__":
    with app.app_context():
        #db.create_all()

        # import hashlib
        # import datetime
        # u = User(name="demo", phone="0123456789", email="demo@gmail.com", username="demo", user_role=UserRole.ADMIN, gender=Gender.MALE,
        # dob=datetime.date(2004, 9, 25),  # Năm, Tháng, Ngày
        # password= str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
        #
        # db.session.add(u)
        # db.session.commit()
        
        # c1 = Category(name="Nghệ thuật - giải trí")
        # c2 = Category(name="Thể thao")
        # c3 = Category(name="Giáo dục - chuyên môn")
        # c4 = Category(name="Giao lưu - xã hội")
        # db.session.add_all([c1, c2, c3, c4])
        # db.session.commit()


        Events = [
        {
            "name": "Hòa nhạc mùa thu",
            "description": "Đêm nhạc giao hưởng với các tác phẩm kinh điển.",
            "datetime": "2025-09-20 19:00",
            "organizer": "Nhà hát Giao Hưởng TP.HCM",
            "vip_price": 1500000,
            "normal_price": 500000,
            "vip_quantity": 100,
            "normal_quantity": 400,
            "address_detail": "Nhà hát Thành phố Hồ Chí Minh, 7 Công Trường Lam Sơn, Quận 1",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040500/hoanhac_tq1qic.jpg",
            "category_id": 1
        },
        {
            "name": "Tech Summit 2025",
            "description": "Hội thảo công nghệ lớn nhất năm với các chuyên gia AI.",
            "datetime": "2025-10-05 09:00",
            "organizer": "FPT Software",
            "vip_price": 2000000,
            "normal_price": 800000,
            "vip_quantity": 200,
            "normal_quantity": 800,
            "address_detail": "Trung tâm Hội nghị Quốc gia, Phạm Hùng, Nam Từ Liêm",
            "province": "Hà Nội",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040500/techsummit_i4qrjm.jpg",
            "category_id": 3
        },
        {
            "name": "Giải Marathon Sài Gòn",
            "description": "Cuộc thi chạy bộ đường dài vì sức khỏe cộng đồng.",
            "datetime": "2025-11-02 05:00",
            "organizer": "Sở Văn hóa & Thể thao TP.HCM",
            "vip_price": 700000,
            "normal_price": 300000,
            "vip_quantity": 1000,
            "normal_quantity": 3000,
            "address_detail": "Phố đi bộ Nguyễn Huệ, Quận 1",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040500/marathon_wxnolm.jpg",
            "category_id": 2
        },
        {
            "name": "Hội chợ Ẩm thực Quốc tế",
            "description": "Trải nghiệm các món ăn đặc sản từ nhiều quốc gia.",
            "datetime": "2025-09-25 10:00",
            "organizer": "Saigon Exhibition Center",
            "vip_price": 500000,
            "normal_price": 200000,
            "vip_quantity": 500,
            "normal_quantity": 2000,
            "address_detail": "Trung tâm Hội chợ Triển lãm Sài Gòn (SECC), Quận 7",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040500/amthuc_bloau1.jpg",
            "category_id": 4
        },
        {
            "name": "Concert Sơn Tùng M-TP",
            "description": "Đêm nhạc hoành tráng với những ca khúc hit.",
            "datetime": "2025-12-15 20:00",
            "organizer": "M-TP Entertainment",
            "vip_price": 3000000,
            "normal_price": 1200000,
            "vip_quantity": 2000,
            "normal_quantity": 10000,
            "address_detail": "Sân vận động Mỹ Đình, Nam Từ Liêm",
            "province": "Hà Nội",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040499/sontungmtp_ucyq6f.jpg",
            "category_id": 1
        },
        {
            "name": "Ngày hội khởi nghiệp",
            "description": "Kết nối startup với nhà đầu tư và mentor.",
            "datetime": "2025-10-18 08:00",
            "organizer": "VietChallenge",
            "vip_price": 1000000,
            "normal_price": 400000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "UP Co-working Space, 268 Lý Thường Kiệt, Quận 10",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040499/khoinghiep_rzkyy7.jpg",
            "category_id": 3
        },
        {
            "name": "Liên hoan phim Việt Nam",
            "description": "Giới thiệu các tác phẩm điện ảnh nổi bật.",
            "datetime": "2025-11-20 18:00",
            "organizer": "Cục Điện ảnh Việt Nam",
            "vip_price": 900000,
            "normal_price": 350000,
            "vip_quantity": 100,
            "normal_quantity": 700,
            "address_detail": "Trung tâm Hội nghị Quốc gia, Phạm Hùng, Nam Từ Liêm",
            "province": "Hà Nội",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040499/lienhoanphim_gj30kl.jpg",
            "category_id": 3
        },
        {
            "name": "Lễ hội Ánh sáng",
            "description": "Không gian ánh sáng rực rỡ tại công viên.",
            "datetime": "2025-12-01 19:00",
            "organizer": "TP.HCM Light Show",
            "vip_price": 600000,
            "normal_price": 250000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Công viên 23/9, Quận 1",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757041622/lehoianhsang_v3vjl3.jpg",
            "category_id": 1
        },
        {
            "name": "Kịch nói Trịnh Công Sơn",
            "description": "Vở kịch về cuộc đời nhạc sĩ Trịnh Công Sơn.",
            "datetime": "2025-09-22 20:00",
            "organizer": "Nhà hát Kịch TP.HCM",
            "vip_price": 800000,
            "normal_price": 300000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Nhà hát Kịch Thành phố, 30 Trần Hưng Đạo, Quận 1",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040499/trinhcongson_q3ngzc.jpg",
            "category_id": 1
        },
        {
            "name": "Comic-Con Việt Nam",
            "description": "Sự kiện cosplay và giao lưu fan manga/anime.",
            "datetime": "2025-11-10 09:00",
            "organizer": "Otaku VN",
            "vip_price": 1200000,
            "normal_price": 500000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "SECC - Trung tâm Hội chợ Triển lãm Sài Gòn, Quận 7",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040499/comic_con_ssawsh.jpg",
            "category_id": 4
        },
        {
            "name": "Hội sách TP.HCM",
            "description": "Ngày hội dành cho những người yêu sách.",
            "datetime": "2025-09-15 08:00",
            "organizer": "NXB Trẻ",
            "vip_price": 200000,
            "normal_price": 50000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Công viên Lê Văn Tám, Quận 1",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040499/hoisach_oshkds.jpg",
            "category_id": 4
        },
        {
            "name": "Giải Esport Liên Minh",
            "description": "Chung kết giải đấu Liên Minh Huyền Thoại.",
            "datetime": "2025-12-22 14:00",
            "organizer": "Garena Việt Nam",
            "vip_price": 1500000,
            "normal_price": 600000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Nhà thi đấu Phú Thọ, 219 Lý Thường Kiệt, Quận 11",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040500/lienminhhuyenthoai_w47w6q.jpg",
            "category_id": 2
        },
        {
            "name": "Triển lãm công nghệ AR/VR",
            "description": "Khám phá xu hướng thực tế ảo mới.",
            "datetime": "2025-10-12 09:00",
            "organizer": "TechWorld Expo",
            "vip_price": 1000000,
            "normal_price": 400000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Trung tâm Hội nghị White Palace, Quận Phú Nhuận",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040498/ar_vr_e29qmk.jpg",
            "category_id": 3
        },
        {
            "name": "Lễ hội bia Đức",
            "description": "Thưởng thức bia và ẩm thực Đức.",
            "datetime": "2025-11-05 17:00",
            "organizer": "German Beer Fest",
            "vip_price": 700000,
            "normal_price": 300000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Công viên Gia Định, Quận Gò Vấp",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040498/lehoibia_tbjius.jpg",
            "category_id": 4
        },
        {
            "name": "Gala thời trang",
            "description": "Sàn diễn thời trang quốc tế với nhiều NTK nổi tiếng.",
            "datetime": "2025-12-28 19:30",
            "organizer": "Vietnam Fashion Week",
            "vip_price": 2500000,
            "normal_price": 1000000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Trung tâm Hội nghị GEM Center, 8 Nguyễn Bỉnh Khiêm, Quận 1",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040498/trinhdienthoitrang_lojoy2.jpg",
            "category_id": 3
        },
        {
            "name": "Workshop AI & Machine Learning",
            "description": "Khóa học chuyên sâu về AI cho sinh viên CNTT.",
            "datetime": "2025-09-30 13:30",
            "organizer": "AI4VN",
            "vip_price": 800000,
            "normal_price": 300000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Đại học Bách Khoa TP.HCM, 268 Lý Thường Kiệt, Quận 10",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040498/workshopAI_kgid6b.jpg",
            "category_id": 3
        },
        {
            "name": "Triển lãm ô tô Việt Nam",
            "description": "Trưng bày các mẫu xe mới nhất.",
            "datetime": "2025-10-22 10:00",
            "organizer": "VAMA",
            "vip_price": 1200000,
            "normal_price": 500000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "SECC - Trung tâm Hội chợ Triển lãm Sài Gòn, Quận 7",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040497/trienlamoto_cjvcjf.jpg",
            "category_id": 3
        },
        {
            "name": "Giải đấu Cờ vua Quốc tế",
            "description": "Quy tụ các kỳ thủ hàng đầu thế giới.",
            "datetime": "2025-11-15 09:00",
            "organizer": "Liên đoàn Cờ Việt Nam",
            "vip_price": 600000,
            "normal_price": 200000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Cung Văn hóa Hữu nghị Việt Xô, 91 Trần Hưng Đạo, Hoàn Kiếm",
            "province": "Hà Nội",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040497/giaicovua_i5w37c.jpg",
            "category_id": 2
        },
        {
            "name": "Hội thảo Marketing số",
            "description": "Chiến lược Digital Marketing cho doanh nghiệp.",
            "datetime": "2025-09-28 09:00",
            "organizer": "Vietnam Marketing Summit",
            "vip_price": 900000,
            "normal_price": 350000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Khách sạn Melia Hà Nội, 44 Lý Thường Kiệt, Hoàn Kiếm",
            "province": "Hà Nội",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040498/hoithaomarketing_i2y0tq.jpg",
            "category_id": 3
        },
        {
            "name": "Giải bóng đá từ thiện",
            "description": "Trận đấu giao hữu gây quỹ học bổng.",
            "datetime": "2025-12-10 16:00",
            "organizer": "Quỹ Vì Tương Lai",
            "vip_price": 500000,
            "normal_price": 150000,
            "vip_quantity": 200,
            "normal_quantity": 1000,
            "address_detail": "Sân vận động Thống Nhất, 30 Nguyễn Kim, Quận 10",
            "province": "Thành phố Hồ Chí Minh",
            "banner": "https://res.cloudinary.com/truongduchoang/image/upload/v1757040497/giaidabongtuthien_cmjpxm.jpg",
            "category_id": 2
        }
        ]
        
        for e in Events:
            temp_event = Event(**e)
            db.session.add(temp_event)

        db.session.commit()
