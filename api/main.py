# This is a sample Python script.
from fastapi import FastAPI

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from app.api.config.scalar_config import router as scalar_router


app = FastAPI()
app.include_router(scalar_router)






# See PyCharm help at https://www.jetbrains.com/help/pycharm/
