# Project: 2D Platformer (Mario-like)

## Stack
- Python 3.12.10
- Pygame 2.5+
- No additional frameworks

## Code style
- Type hints везде где возможно
- Классы для сущностей (Player, Enemy, Tile)
- Константы выносим в settings.py
- Логика и отрисовка разделены

## Game design
- Вид сбоку, 2D
- Управление: стрелки + пробел (прыжок)
- Гравитация, прыжки переменной высоты
- Тайловые уровни (16x16 или 32x32 пикселя)
- Камера следует за игроком
- Враги с простым AI (патрулирование)
- Монетки, счёт, жизни

## Architecture
- Главный цикл: input → update → collisions → render
- FPS: 60
- Уровни описываются в txt-файлах: '.' = пусто, '#' = блок, 'P' = старт, 'E' = враг, 'C' = монета