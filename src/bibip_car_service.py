import os
from datetime import datetime
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.cars_file_path = os.path.join(self.root_directory_path,
                                           "cars.txt")
        self.cars_index_file_path = os.path.join(self.root_directory_path,
                                                 "cars_index.txt")
        self.models_file_path = os.path.join(self.root_directory_path,
                                             "models.txt")
        self.models_index_file_path = os.path.join(
            self.root_directory_path, "models_index.txt")
        self.sales_file_path = os.path.join(self.root_directory_path,
                                            "sales.txt")
        self.sales_index_file_path = os.path.join(
            self.root_directory_path, "sales_index.txt")

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        if not os.path.exists(self.models_file_path):
            open(self.models_file_path, "w").close()
        if not os.path.exists(self.models_index_file_path):
            open(self.models_index_file_path, "w").close()
        with open(self.models_file_path, "a") as models_file, open(
                self.models_index_file_path, "r+") as models_index_file:
            models_file.seek(0, os.SEEK_END)
            position = models_file.tell()
            models_file.write(f"{model.id}|{model.name}|{model.brand}\n")
            models_index_file.seek(0)
            index_lines = models_index_file.readlines()
            index_lines.append(f"{model.id}|{position}\n")
            index_lines.sort()
            models_index_file.seek(0)
            models_index_file.truncate(0)
            models_index_file.writelines(index_lines)
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        if not os.path.exists(self.cars_file_path):
            open(self.cars_file_path, "w").close()
        if not os.path.exists(self.cars_index_file_path):
            open(self.cars_index_file_path, "w").close()
        with open(self.cars_file_path, "a") as cars_file, open(
                self.cars_index_file_path, "r+") as cars_index_file:
            cars_file.seek(0, os.SEEK_END)
            position = cars_file.tell()
            cars_file.write(
                f"{car.vin}|{car.model}|{car.price}|{car.date_start}|"
                f"{car.status}\n")
            cars_index_file.seek(0)
            index_lines = cars_index_file.readlines()
            index_lines.append(f"{car.vin}|{position}\n")
            index_lines.sort()
            cars_index_file.seek(0)
            cars_index_file.truncate(0)
            cars_index_file.writelines(index_lines)
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        if not os.path.exists(self.sales_file_path):
            open(self.sales_file_path, "w").close()
        if not os.path.exists(self.sales_index_file_path):
            open(self.sales_index_file_path, "w").close()
        with open(self.sales_file_path, "a") as sales_file, open(
                self.sales_index_file_path, "r+") as sales_index_file:
            sales_file.seek(0, os.SEEK_END)
            position = sales_file.tell()
            sales_file.write(
                f"{sale.sales_number}|{sale.car_vin}|{sale.sales_date}|"
                f"{sale.cost}\n")
            sales_index_file.seek(0)
            index_lines = sales_index_file.readlines()
            index_lines.append(f"{sale.sales_number}|{position}\n")
            index_lines.sort()
            sales_index_file.seek(0)
            sales_index_file.truncate(0)
            sales_index_file.writelines(index_lines)
        with open(self.cars_index_file_path, "r") as cars_index_file:
            for line in cars_index_file:
                index_vin, position = line.strip().split("|")
                if index_vin == sale.car_vin:
                    car_position = int(position)
                    break
        if car_position is not None:
            with open(self.cars_file_path, "r+") as cars_file:
                cars_file.seek(car_position)
                car_data = cars_file.readline().strip().split("|")
                car = Car(
                    vin=car_data[0],
                    model=int(car_data[1]),
                    price=Decimal(car_data[2]),
                    date_start=datetime.fromisoformat(car_data[3]),
                    status=CarStatus.sold
                )
                new_car_data = (
                    f"{car.vin}|{car.model}|{car.price}|"
                    f"{car.date_start}|{car.status}\n")
                cars_file.seek(car_position)
                cars_file.write(new_car_data)
                return car
        return None

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        available_cars: list[Car] = []
        with open(self.cars_file_path, "r") as cars_file:
            available_cars = [
                Car(
                    vin=car_data[0],
                    model=int(car_data[1]),
                    price=Decimal(car_data[2]),
                    date_start=datetime.fromisoformat(car_data[3]),
                    status=CarStatus(car_data[4])
                )
                for line in cars_file
                for car_data in [line.strip().split("|")]
                if CarStatus(car_data[4]) == status
            ]
        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        with open(self.cars_index_file_path, "r") as cars_index_file:
            for line in cars_index_file:
                index_vin, position = line.strip().split("|")
                if index_vin == vin:
                    car_position = int(position)
                    break
            else:
                return None
        with open(self.cars_file_path, "r") as cars_file:
            cars_file.seek(car_position)
            car_data = cars_file.readline().strip().split("|")
            car = Car(
                vin=car_data[0],
                model=int(car_data[1]),
                price=Decimal(car_data[2]),
                date_start=datetime.fromisoformat(car_data[3]),
                status=CarStatus(car_data[4])
            )
        with open(self.models_index_file_path, "r") as models_index_file:
            for line in models_index_file:
                model_id, position = line.strip().split("|")
                if int(model_id) == int(car.model):
                    model_position = int(position)
                    break
        with open(self.models_file_path, "r") as models_file:
            models_file.seek(model_position)
            model_data = models_file.readline().strip().split("|")
            model = Model(id=int(model_data[0]), name=model_data[1],
                          brand=model_data[2])
        sales_date = None
        sales_cost = None
        if car.status == CarStatus.sold:
            with open(self.sales_file_path, "r") as sales_file:
                for line in sales_file:
                    (sales_number, sales_vin, sale_date,
                     sale_cost) = line.strip().split("|")
                    if sales_vin == car.vin:
                        sales_date = datetime.strptime(
                            sale_date, "%Y-%m-%d %H:%M:%S")
                        sales_cost = Decimal(sale_cost)
                        break
        return CarFullInfo(
            vin=car.vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=car.price,
            date_start=car.date_start,
            status=car.status,
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        with open(self.cars_index_file_path, "r") as cars_index_file:
            for i, line in enumerate(cars_index_file):
                index_vin, position = line.strip().split("|")
                if index_vin == vin:
                    car_position = int(position)
                    break
        with open(self.cars_file_path, "r+") as cars_file:
            cars_file.seek(car_position)
            car_data = cars_file.readline().strip().split("|")
            updated_car_data = (
                f"{new_vin}|{car_data[1]}|{car_data[2]}|"
                f"{car_data[3]}|{car_data[4]}\n")
            cars_file.seek(car_position)
            cars_file.write(updated_car_data)
            cars_file.flush()
        with open(self.cars_index_file_path, "r") as cars_index_file:
            index_lines = cars_index_file.readlines()
        with open(self.cars_index_file_path, "w") as cars_index_file:
            for line in index_lines:
                index_vin, position = line.strip().split("|")
                if index_vin == vin:
                    cars_index_file.write(f"{new_vin}|{position}\n")
                else:
                    cars_index_file.write(line)
        car = Car(
            vin=new_vin,
            model=int(car_data[1]),
            price=Decimal(car_data[2]),
            date_start=datetime.fromisoformat(car_data[3]),
            status=CarStatus(car_data[4])
        )
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        with open(self.sales_index_file_path, "r") as sales_index_file:
            for line in sales_index_file:
                index_sales_number, position = line.strip().split("|")
                if index_sales_number == sales_number:
                    sales_position = int(position)
                    break
        with open(self.sales_file_path, "r") as sales_file:
            sales_file.seek(sales_position)
            sales_data = sales_file.readline().strip().split("|")
            vin = sales_data[1]
        with open(self.sales_file_path, "r") as sales_file:
            updated_sales_data = [
                line for line in sales_file
                if line.strip().split("|")[0] != sales_number]
        with open(self.sales_file_path, "w") as sales_file:
            sales_file.writelines(updated_sales_data)
        with open(self.sales_file_path, "r") as sales_file:
            index_data = [
                f"{line.strip().split('|')[0]}|{pos}\n"
                for pos, line in enumerate(sales_file.readlines())]
            index_data.sort()
        with open(self.sales_index_file_path, "w") as sales_index_file:
            sales_index_file.writelines(index_data)
        with open(self.cars_index_file_path, "r") as cars_index_file:
            for line in cars_index_file:
                index_vin, position = line.strip().split("|")
                if index_vin == vin:
                    car_position = int(position)
                    break
        with open(self.cars_file_path, "r+") as cars_file:
            cars_file.seek(car_position)
            car_data = cars_file.readline().strip().split("|")
            car = Car(
                vin=car_data[0],
                model=int(car_data[1]),
                price=Decimal(car_data[2]),
                date_start=datetime.fromisoformat(car_data[3]),
                status=CarStatus.available
            )
            updated_car_data = (
                f"{car.vin}|{car.model}|{car.price}|"
                f"{car.date_start.isoformat()}|{car.status}\n")
            cars_file.seek(car_position)
            cars_file.write(updated_car_data)
        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        model_sales_count: dict[str, int] = {}
        model_prices: dict[str, float] = {}
        model_data_cache: dict[str, Model] = {}
        with open(self.sales_file_path, "r") as sales_file:
            for line in sales_file:
                vin = line.strip().split("|")[1]
                with open(self.cars_index_file_path, "r") as cars_index_file:
                    for car_index_line in cars_index_file:
                        index_vin, position = car_index_line.strip().split("|")
                        if index_vin == vin:
                            car_position = int(position)
                            break
                with open(self.cars_file_path, "r") as cars_file:
                    cars_file.seek(car_position)
                    car_data = cars_file.readline().strip().split("|")
                    model_id = car_data[1]
                    price = float(car_data[2])
                    model_sales_count[model_id] = (
                        model_sales_count.get(model_id, 0) + 1)
                    model_prices[model_id] = price
        sorted_models = sorted(
            model_sales_count.items(),
            key=lambda item: (item[1], model_prices.get(item[0], 0.0)),
            reverse=True,
        )[:3]
        top_models: list[ModelSaleStats] = []
        for model_id, sales_count in sorted_models:
            if model_id in model_data_cache:
                model = model_data_cache[model_id]
            else:
                with open(
                        self.models_index_file_path, "r") as models_index_file:
                    for line in models_index_file:
                        index_model_id, position = line.strip().split("|")
                        if index_model_id == model_id:
                            model_position = int(position)
                            break
                with open(self.models_file_path, "r") as models_file:
                    models_file.seek(model_position)
                    model_data = models_file.readline().strip().split("|")
                    model = Model(
                        id=int(model_data[0]),
                        name=model_data[1],
                        brand=model_data[2])
                    model_data_cache[model_id] = model
            top_models.append(
                ModelSaleStats(
                    car_model_name=model.name,
                    brand=model.brand,
                    sales_number=sales_count
                )
            )
        return top_models
