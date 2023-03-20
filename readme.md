#
python -m venv venv
# 
source venv/scripts/activate
#  
pip install -r requirements.txt
#  create .env file in root folder
##  Test
TEST_HOST=127.0.0.1
TEST_PORT=8000

##  DB_SETTINGS
DB_HOST=localhost
DB_USER=db_user
DB_PASS=123456
DB_PORT=5432
DB_DRIVER=postgresql
DB_NAME=db_name

## Security token settings
SECRET_JWT_KEY=     # < openssl rand -hex 32
TOKEN_LIFETIME_IN_MINTUTES=30
ENCRYPTING_ALGORITHM=HS256

## Password security settings
HASHING_SCHEME=bcrypt
##  Pepper must be exactly 22 symbols. 
PEPER_SECRET=     # < openssl rand -hex 11
