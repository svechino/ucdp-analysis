import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
df1 = pd.read_csv(r"C:\Users\97252\Desktop\Practicum\Charm Data\GEDEvent_v24_01_24_06.csv")
df2 = pd.read_csv(r"C:\Users\97252\Desktop\Practicum\Charm Data\ged241-csv\GEDEvent_v24_1.csv")

# Объединение данных
combined_data = pd.concat([df1, df2], ignore_index=True)

# Проверка объединенных данных
print(combined_data.info())
print(combined_data.head())

# Проверка на пропущенные значения
missing_values = combined_data.isnull().sum()
print("Пропущенные значения в объединенных данных:")
print(missing_values[missing_values > 0])

# Анализ распределения событий по годам
combined_data['year'].value_counts().sort_index().plot(kind='bar', figsize=(12, 6), title='Распределение событий по годам')
plt.xlabel('Год')
plt.ylabel('Количество событий')
plt.show()

# Анализ типов насилия
combined_data['type_of_violence'].value_counts().plot(kind='bar', figsize=(8, 6), title='Распределение типов насилия')
plt.xlabel('Тип насилия')
plt.ylabel('Количество событий')
plt.show()

# Анализ распределения событий по регионам
region_distribution = combined_data['region'].value_counts()
region_distribution.plot(kind='bar', figsize=(10, 6), title='Распределение событий по регионам')
plt.xlabel('Регион')
plt.ylabel('Количество событий')
plt.show()

# Также можно сделать географическое распределение событий по регионам
plt.figure(figsize=(12, 8))
for region in combined_data['region'].unique():
    region_data = combined_data[combined_data['region'] == region]
    plt.scatter(region_data['longitude'], region_data['latitude'], alpha=0.5, label=region)

plt.title('Географическое распределение событий по регионам')
plt.xlabel('Долгота')
plt.ylabel('Широта')
plt.legend()
plt.show()

# Анализ смертности
combined_data[['deaths_a', 'deaths_b', 'deaths_civilians', 'best', 'high', 'low']].plot(kind='box', figsize=(10, 6), title='Анализ смертности')
plt.show()

# Сохранение объединенных данных в файл CSV
combined_data.to_csv(r"C:\Users\97252\Desktop\Practicum\Charm Data\combined_ged_event_data.csv", index=False)