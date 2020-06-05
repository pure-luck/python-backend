db = {
    'user': 'root',
    'password': 'aksen123',
    'host': 'db1.cgqwja2ala0t.ap-northeast-2.rds.amazonaws.com',
    'port': 3306,
    'database': 'db1'
}
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
S3_BUCKET = "python-backend"
S3_ACCESS_KEY = "AKIAYRG6NJ5EW2GIFRF5"
S3_SECRET_KEY = "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"
S3_REGION = "ap-northeast-2"
S3_BUCKET_URL = f"http://{S3_BUCKET}.s3.amazonaws.com/"
JWT_SECRET_KEY        = 'SOME_SUPER_SECRET_KEY'
JWT_EXP_DELTA_SECONDS = 7 * 24 * 60 * 60

test_db = {
    'user'     : 'root',
    'password' : '5261',
    'host'     : 'localhost',
    'port'     : 3306,
    'database' : 'ob'
}
test_config = {
    'DB_URL' : f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY'        : 'SOME_SUPER_SECRET_KEY',
    'JWT_EXP_DELTA_SECONDS' : 7 * 24 * 60 * 60,
    'S3_BUCKET'             : "test",
    'S3_ACCESS_KEY'         : "test_acces_key",
    'S3_SECRET_KEY'         : "test_secret_key",
    'S3_BUCKET_URL'         : f"https://s3.ap-northeast-2.amazonaws.com/test/"
}