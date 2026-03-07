DEBUG = True
PORT = 9528
IMPORT_CSV = "./ledger.csv"
DB_NAME = "data/ledger.db"
DB_SCHEEMA = "data/create_db.sql"
INIT_DATA = "data/private_data.sql"
SQLALCHEMY_DATABASE_URI = "sqlite:///data/ledger.db?check_same_thread=False"
SQLALCHEMY_TRACK_MODIFICATIONS = True
INVOICE_CARD_NO = "/ABC0000"
INVOICE_PASSWORD = "a1234567"
INVOICE_APP_ID = "EINV7202108130242"
INVOICE_SKIP = ["/VRYU92B", "/YV7E28T", "1767606528"]
