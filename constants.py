from dotenv import dotenv_values

credentials = dotenv_values(".env.secret")

print(credentials)

BOT_TOKEN = credentials["BOT_API_TOKEN"]