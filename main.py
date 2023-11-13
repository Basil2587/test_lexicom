import re

from fastapi import FastAPI, HTTPException
from redis import Redis
from pydantic import BaseModel, validator

app = FastAPI()
redis_client = Redis(host='redis', port=6379)  # Подключение к Redis


class UpdatedAddressInfo(BaseModel):
    phone: str
    address: str

    @validator("phone")
    def validate_phone(cls, phone):
        # Проверка, что номер телефона состоит из 11 цифр и начинается с "8" или "+7"
        if not re.match(r'^(\+7|8)\d{10}$', phone):
            raise ValueError('Неверный формат номера телефона')
        return phone


@app.get("/check_data")
def check_data(phone: str):
    # Получение данных
    address = redis_client.get(phone)

    if not address:
        raise HTTPException(status_code=404, detail="Адрес не найден")

    return {"address": address.decode()}


@app.post("/write_data")
def write_data(address_request: UpdatedAddressInfo):
    # Проверка валидности модели
    if not address_request.address:
        return {"message": "❌ Укажите адрес"}

    phone = address_request.phone
    address = address_request.address
    if redis_client.get(phone):
        # Если номер уже существует, обновляем адрес
        redis_client.set(phone, address)
        return {"message": "⚠ Номер уже существовал. Адрес успешно изменен"}

    redis_client.set(phone, address)
    return {"message": "✅ Данные успешно записаны"}


@app.put("/write_data")
def update_address(address_request: UpdatedAddressInfo):
    # Обновляем данные
    phone = address_request.phone
    address = address_request.address
    existing_address = redis_client.get(phone)

    if not existing_address:
        raise HTTPException(status_code=404, detail="Номер не найден")

    redis_client.set(phone, address)
    return {"message": "✅ Адрес успешно обновлен"}
