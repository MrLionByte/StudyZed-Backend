from firebase_admin import credentials, messaging, initialize_app

class FCMServices:
    def __init__(self):
        pass
        # cred = credentials.Certificate({
        #     'type': 'service_account',
        #     "project_id": "study-zed-notifications",
        #     "private_key_id": "6d4bfc68f8715ead7b98eff10d907c846585b836",
        #     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCvYF47vQXaglr7\nodQr6oCT09ozob7JSs3u13Q7WKzZmcZEsnHjnE+yDtAD2QRhbBiDXE52odx28YC8\njiRsYuGFCGBOnIiU1ZJ0vpnwTbXPj82flyWnVMoyDQdpXJ3xwLoV5CjSTXznC0wD\nXrEDMQf2Cl7ywY1C5Zhc+Mnl3rBki0HGrjj/dfM4FHWaj5Fk0q7xLqahp41VYX44\nLg5TxK+PTWXbrJnjFH2JLmG665CqLuvLSwE+x4/2hKA6bS/KOZ5QWJKvEedhSVau\n7jkw2EbWALzx3NdnE5twLbSCJrQzcXyXemURmCVn+gXSSNqfvacB6FMu6lK02cxx\nIQemR+x1AgMBAAECggEAEhvfecf/D+eQRoBuJ1S7ucf74C347ycSvvFaFqYFlHiH\nm7YDWDnelCe/EflO4FJoRj7PTqT7CKsk8b4JrnQYDlkQPL3MGqDiUmdl/4VpWx6M\nYHNxLLyZc56bH9AznPAbfEGGzORkcSUI+yYZcsIVgjHi86p0ZYPN/kz66AoHvnHj\nkLyDeWX6Z5rr/zcYF7FGpErsOoQwsyCwsgnAcC0yx8c5+A7gMcH2Vji3NGzdQcx+\ncmzYaSLzvavEPIpZUf66RTFHaH4wMnybgA4PCat4zF2cqcUWQCj8UE4dNAFF/mMI\nIlhAY7WQmfMoiF+7eYIw7c13ybrTSkzRVJf2VS9TBwKBgQDeP+IjCrLsTlUZRDmR\nL7ehAldL8dSgNY7M0neocmVh71CpScv8vmndQ0Tnxd2wT66ZRqGC7EcT8IJY+zmc\nZmXBrV7yzhzF5iDpqI0JjbRP7nzyzlYVaYATBUda2Ml1bmhMpT+Q6oEsRMwZerI2\n2eDeS5wtu2iY/oK3/TvA22kx2wKBgQDKAkH/1DyDESqUMAlFP5ojE8K2Bc0ki6EX\nn5zlNI3+NwdIICEanPCu4YqfBMuI+shXP/8Tp+BK+PuKtF6WS89pw25emX5Z1ACI\n8YOqE72Cm/29KU4M3XgGfjbwmP9aFT1/qhYoFFPzAinDOfBW+C6rN7+S7eGvodhQ\nWmZhKRdz7wKBgEJo9mqgJMzFr1oIb+c5Sfabm3g+/9kLh+seLNExtaeo+gJL4d9Z\nCosqManMDy1C8hos59AWSDrmEB0EnLdmRZu08X0+J4ze8hC/47zqEeocikuHamOl\njbahSiwUQUaMwi+85RypZgXTXOV0K1KGklH6Z+WmbV/iFS9jRPqg1XMnAoGBAKgM\nHslqzngeNLSYDW49DcW2b5kq1FBdk8JqNoP6J1Feh8E5cTCJdDOXTtEglQ07yqPC\nijjYw966p87oY3NWV5JdUJiDyjeCBHvnpic7SsC3cesFzHcpWerU3nFiZbKTzthA\nLzRiTL/wgbt1nHlM9s3aj5T0LXYFBkU6Hsce/vKjAoGAfW45VBV61r6H2nSYywQ4\nGlWW5ZJUxg9KRDQWG5A6oVA00KJrs1vOU4vya+TEt8/efAvdQQ81GJXdhucSQfL5\n0O+IXqTKBUpELCSesBD7fnBmohmdb9O92WRKe+r3hxnCeezQHwye7NAnv+IOyShf\n7W+YiMdVVAPnKimkJHjacXQ=\n-----END PRIVATE KEY-----\n",
        #     "client_email": "firebase-adminsdk-fbsvc@study-zed-notifications.iam.gserviceaccount.com",
        #     "client_id": "110466895487247826694",
        #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        #     "token_uri": "https://oauth2.googleapis.com/token",
        #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40study-zed-notifications.iam.gserviceaccount.com",
        #     "universe_domain": "googleapis.com"
        # })
        # initialize_app(cred)

    def send_message(self, title, message, tokens):
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=message
                ),
                tokens=tokens
            )
            response = messaging.send_multicast(message)
            return {"success": True, "message": response}
        except Exception as e:
            return {"error": str(e)}