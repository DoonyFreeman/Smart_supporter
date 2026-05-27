import matplotlib.pyplot as plt

# Данные для построения (включая крайние точки для замкнутости)
x = [3, 5, 7, 9, 11, 13, 15]
y = [0, 0.06, 0.18, 0.14, 0.44, 0.18, 0]

plt.figure(figsize=(8, 5))

# Строим линии и выделяем точки маркерами
plt.plot(x, y, marker='o', color='b', linestyle='-', linewidth=2, label='Полигон частот')
# Закрашиваем область под графиком для наглядности (опционально)
plt.fill_between(x, y, color='blue', alpha=0.1)

# Настройка осей и сетки
plt.title('Полигон относительных частот', fontsize=14, fontweight='bold')
plt.xlabel('Варианты (x)', fontsize=12)
plt.ylabel('Относительные частоты (w)', fontsize=12)
plt.xticks(x)  # отображаем именно наши значения на оси X
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Показываем график
plt.show()