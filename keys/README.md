# Keys

All keys are stored in this folder

- To generate the public/private.pem files please run `backend/utils/key_generator.py`
- Generate admin password hash using `backend/utils/gen_admin_pass.py`
- Also create a MongoKeys.json and place your username and password in the following format - 

```
{
    "UserName": "UserName",
    "PSWD": "PSWD"
}
```