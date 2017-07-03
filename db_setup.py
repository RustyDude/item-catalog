from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user = User(
    name="Sports Enthusiast",
    email="sporty@sports.com",
    picture='https://thumbs.dreamstime.com/x/tired-sportsman-17939248.jpg'
)
session.add(user)
session.commit()

print "added user!"

# Create dummy Categories
categories = [Category(name='Soccer'),
              Category(name='Basketball'),
              Category(name='Baseball'),
              Category(name='Frisbee'),
              Category(name='Snowboarding'),
              Category(name='Rock Climbing'),
              Category(name='Foosball'),
              Category(name='Skating'),
              Category(name='Hockey')
              ]

for category in categories:
    session.add(category)
    session.commit()

print "added catergories!"

# Create dummy Items
items = [
    CategoryItem(user_id=1, name="Soccer Cleats",
                 description="Something About Soccer Cleats",
                 category_id=1),
    CategoryItem(user_id=1, name="Jersey",
                 description="Something About Jersey",
                 category_id=1),
    CategoryItem(user_id=1, name="Bat",
                 description="Something About Bat",
                 category_id=3),
    CategoryItem(user_id=1, name="Frisbee",
                 description="Something About Frisbee",
                 category_id=4),
    CategoryItem(user_id=1, name="Shinguards",
                 description="Something About Shinguards",
                 category_id=1),
    CategoryItem(user_id=1, name="Two Shinguards",
                 description="Something About Two Shinguards",
                 category_id=1),
    CategoryItem(user_id=1, name="Snowboard",
                 description="Something About Snowboard",
                 category_id=5),
    CategoryItem(user_id=1, name="Googles",
                 description="Something About Googles",
                 category_id=5),
    CategoryItem(user_id=1, name="Stick",
                 description="Something About Stick",
                 category_id=9)
]

for item in items:
    session.add(item)
    session.commit()

print "added items!"
