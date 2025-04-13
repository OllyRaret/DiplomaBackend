class StartupStage:
    WAITING = 'waiting'
    IN_PROGRESS = 'in_progress'
    LAUNCH = 'launch'
    ANALYSIS = 'analysis'
    COMPLETED = 'completed'

    CHOICES = [
        (WAITING, 'Ожидание'),
        (IN_PROGRESS, 'В процессе'),
        (LAUNCH, 'Запуск'),
        (ANALYSIS, 'Анализ результатов'),
        (COMPLETED, 'Завершён'),
    ]
