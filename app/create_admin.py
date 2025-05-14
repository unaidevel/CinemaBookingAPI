from app.models import UserInDb
from app.database import SessionDep
from uuid import uuid4
from datetime import date
from passlib.context import CryptContext
from app.auths.auth import pwd_context
from sqlmodel import select
from sqlmodel import Session
from app.database import engine


"""
SCRIPT TO CREATE USERS WITH DIFFERENT ROLES
"""

"""
INSTRUCTIONS:
Enter on docker container and execute the script. Be sure the locations match.
-'docker exec -it cinemabookingapi sh'(alpine)    or 'docker exec -it cinemabookingapi bash' 
-'python3 -m app.create_admin'
"""



session = Session(engine)



admin_user = UserInDb(
    id=uuid4(),
    username='', #New username
    full_name='', 
    email='', #New email
    role='admin', #The role, can be staff
    birth_date=date(), #New birth date  #Format:Y,M,D
    is_active=True,
    disabled=False,
    hashed_password=pwd_context.hash('password')
)

existing_user = session.exec(select(UserInDb).where(UserInDb.email == admin_user.email)).first()

if not existing_user:
    session.add(admin_user)
    session.commit()
    print('Admin user created')
else:
    print('Admin user already exists')



session.close()


