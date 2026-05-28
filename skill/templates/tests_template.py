"""
Шаблон tests.py для лабораторных работ.

Содержит по одному примеру каждого паттерна тестирования.
Claude Code на этапе 2 использует этот файл как образец стиля и структуры,
заменяя содержимое тестов на логику из lab_spec.md.

Ключевые соглашения:
- Один класс на одно задание из lab_spec.md
- Фикстура student_module берётся из conftest.py (scope='session')
- Бонусные тесты скипаются через pytest.skip если переменная не определена
- Имена тестовых функций должны совпадать с ключами в TEST_POINTS в conftest.py
"""

import pytest
import numpy as np
import pandas as pd
import os


# импорт exercises происходит через фикстуру student_module из conftest.py
# НЕ импортировать exercises напрямую через import


# ===========================================================================
# Паттерн 1: тест переменной
# ===========================================================================

class TestVariableExample:
    """Пример: проверка переменной-датафрейма"""

    def test_df_loaded(self, student_module):
        """Переменная определена, является DataFrame, не пустая"""
        assert hasattr(student_module, 'df'), \
            "Переменная df не определена"
        assert student_module.df is not None, \
            "Переменная df равна None"
        assert isinstance(student_module.df, pd.DataFrame), \
            "df должен быть pandas DataFrame"
        assert len(student_module.df) > 0, \
            "df не должен быть пустым"

    def test_df_no_nan(self, student_module):
        """DataFrame не содержит пропусков"""
        assert student_module.df.isnull().sum().sum() == 0, \
            "df содержит пропущенные значения (NaN)"

    def test_array_shape(self, student_module):
        """Пример: проверка размерности numpy-массива"""
        arr = student_module.observations
        assert isinstance(arr, np.ndarray), \
            "observations должен быть np.ndarray"
        assert arr.ndim == 2, \
            f"observations должен быть двумерным, получено ndim={arr.ndim}"
        assert arr.shape[1] == 1, \
            f"observations должен иметь форму (n, 1), получено shape={arr.shape}"
        assert not np.isnan(arr).any(), \
            "observations содержит NaN"


# ===========================================================================
# Паттерн 2: тест функции
# ===========================================================================

class TestFunctionExample:
    """Пример: проверка функции, возвращающей результат вычисления"""

    def test_function_returns_correct_type(self, student_module):
        """Функция возвращает корректный тип"""
        func = getattr(student_module, 'compute_something', None)
        assert func is not None, "Функция compute_something не определена"

        result = func(np.array([1.0, 2.0, 3.0]))
        assert isinstance(result, np.ndarray), \
            f"compute_something должна возвращать np.ndarray, получено {type(result)}"

    def test_function_output_shape(self, student_module):
        """Выход функции имеет правильную размерность"""
        func = student_module.compute_something
        x = np.array([1.0, 2.0, 3.0])
        result = func(x)
        assert result.shape == x.shape, \
            f"Ожидалась форма {x.shape}, получено {result.shape}"

    def test_function_output_values(self, student_module):
        """Выход функции корректен на известном входе"""
        func = student_module.compute_something
        x = np.array([1.0, 2.0, 3.0])
        result = func(x)
        expected = np.array([...])  # подставить ожидаемые значения
        assert np.allclose(result, expected, rtol=0.05), \
            f"Значения не совпадают: ожидалось {expected}, получено {result}"

    def test_function_returns_figure(self, student_module):
        """Пример: проверка функции, возвращающей график"""
        import matplotlib
        func = getattr(student_module, 'plot_something', None)
        assert func is not None, "Функция plot_something не определена"

        try:
            fig = func(np.array([1.0, 2.0, 3.0]))
        except Exception as e:
            pytest.fail(f"plot_something завершилась с ошибкой: {e}")

        assert isinstance(fig, matplotlib.figure.Figure), \
            f"plot_something должна возвращать matplotlib.figure.Figure, получено {type(fig)}"


# ===========================================================================
# Паттерн 3: тест класса
# ===========================================================================

class TestClassExample:
    """Пример: проверка пользовательского класса"""

    def test_class_exists(self, student_module):
        """Класс определён"""
        assert hasattr(student_module, 'CustomClass'), \
            "Класс CustomClass не определён"

    def test_class_attributes(self, student_module):
        """Экземпляр класса имеет нужные атрибуты"""
        CustomClass = student_module.CustomClass
        # тестовые входные данные из lab_spec.md
        params = [np.ones((2, 1)), np.zeros(1)]
        obj = CustomClass(params, lr=0.01)

        assert hasattr(obj, 'lr'), "CustomClass не имеет атрибута lr"
        assert obj.lr > 0, "Атрибут lr должен быть > 0"

    def test_class_method_mutates_state(self, student_module):
        """Метод изменяет состояние объекта (in-place)"""
        CustomClass = student_module.CustomClass
        W = np.ones((2, 1))
        b = np.zeros(1)
        params = [W, b]
        obj = CustomClass(params, lr=0.01)

        x_batch = np.array([[1.0, 2.0], [3.0, 4.0]])
        y_batch = np.array([0.5, 1.5])
        w_before = params[0].copy()

        try:
            obj.step(x_batch, y_batch)
        except Exception as e:
            pytest.fail(f"CustomClass.step() завершился с ошибкой: {e}")

        assert not np.allclose(params[0], w_before), \
            "step() не обновил параметры. Убедитесь, что обновление происходит in-place."

    def test_class_method_returns_value(self, student_module):
        """Пример: метод возвращает значение корректного типа и размерности"""
        CustomClass = student_module.CustomClass
        obj = CustomClass(n_components=3)
        obs = np.random.randn(200, 1)
        obj.fit(obs)

        result = obj.decode(obs)
        assert isinstance(result, np.ndarray), \
            f"decode() должен возвращать np.ndarray, получено {type(result)}"
        assert len(result) == len(obs), \
            f"Длина результата {len(result)} не совпадает с длиной входа {len(obs)}"
        assert result.min() >= 0 and result.max() < 3, \
            "Значения decode() должны быть в диапазоне [0, n_components-1]"


# ===========================================================================
# Паттерн 4: тест артефакта
# ===========================================================================

class TestArtifactExample:
    """Пример: проверка файла-артефакта, сохранённого студентом"""

    def test_artifact_exists(self):
        """Файл артефакта существует"""
        assert os.path.exists('artifact.json'), \
            "Файл artifact.json не найден. Убедитесь, что вы сохранили артефакт."

    def test_artifact_loads(self):
        """Артефакт загружается без ошибок"""
        import json
        try:
            with open('artifact.json') as f:
                data = json.load(f)
        except Exception as e:
            pytest.fail(f"Не удалось загрузить artifact.json: {e}")

    def test_artifact_structure(self):
        """Артефакт содержит нужные ключи"""
        import json
        with open('artifact.json') as f:
            data = json.load(f)
        required_keys = ['metric1', 'metric2', 'n_params']
        for key in required_keys:
            assert key in data, f"В artifact.json отсутствует ключ '{key}'"

    def test_artifact_values(self):
        """Числовые значения в артефакте корректны"""
        import json
        with open('artifact.json') as f:
            data = json.load(f)
        assert data['metric1'] > 0, \
            "metric1 должен быть положительным"
        # Числовое равенство с допуском rtol=0.05
        expected = 42.0  # подставить ожидаемое значение из lab_spec.md
        assert abs(data['metric2'] - expected) < 0.05 * abs(expected), \
            f"metric2 ожидалось ~{expected}, получено {data['metric2']}"


# ===========================================================================
# Паттерн 5: бонусные задания
#
# Правило: один класс на одно бонусное задание — так же как для обычных.
# Общий класс TestBonus НЕ используется.
# Имена классов: TestBonus1, TestBonus2 и т.п. (или по названию задания).
# Каждый тест внутри начинается с проверки наличия переменной и pytest.skip.
# ===========================================================================

class TestBonus1:
    """[Бонус *] Пример бонусного задания с переменной"""

    def test_bonus_variable_exists(self, student_module):
        """[Бонус *] Переменная определена и не None"""
        if not hasattr(student_module, 'bonus_result') \
                or student_module.bonus_result is None:
            pytest.skip("Бонусное задание * не выполнено")
        # Если дошли сюда — переменная есть, проверяем тип
        assert isinstance(student_module.bonus_result, np.ndarray), \
            "bonus_result должен быть np.ndarray"

    def test_bonus_variable_values(self, student_module):
        """[Бонус *] Значения переменной корректны"""
        if not hasattr(student_module, 'bonus_result') \
                or student_module.bonus_result is None:
            pytest.skip("Бонусное задание * не выполнено")
        assert len(student_module.bonus_result) > 0, \
            "bonus_result не должен быть пустым"


class TestBonus2:
    """[Бонус **] Пример бонусного задания с функцией"""

    def test_bonus_function_exists(self, student_module):
        """[Бонус **] Функция определена"""
        if not hasattr(student_module, 'bonus_func') \
                or student_module.bonus_func is None:
            pytest.skip("Бонусное задание ** не выполнено")
        assert callable(student_module.bonus_func), \
            "bonus_func должна быть вызываемой функцией"

    def test_bonus_function_output(self, student_module):
        """[Бонус **] Функция возвращает корректный результат"""
        if not hasattr(student_module, 'bonus_func') \
                or student_module.bonus_func is None:
            pytest.skip("Бонусное задание ** не выполнено")
        result = student_module.bonus_func(np.array([1.0, 2.0, 3.0]))
        assert result > 0.8, \
            f"Ожидалось значение > 0.8, получено {result}"
