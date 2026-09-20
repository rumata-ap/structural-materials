Установка и настройка
=====================

Требования
----------

* **Python**: версия 3.9 или выше.
* **NumPy**: версия 1.20 или выше.

Установка библиотеки
--------------------

Для установки библиотеки из исходного кода в режиме разработки:

.. code-block:: bash

   git clone https://github.com/rumata-ap/structural-materials.git
   cd structural-materials
   pip install -e .

Установка дополнительных зависимостей
-------------------------------------

Интерактивные блокноты (Jupyter & ipywidgets)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Если планируется работа с интерактивными блокнотами из каталога ``notebooks/``:

.. code-block:: bash

   pip install -e ".[notebooks]"

Сборка документации (Sphinx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для локальной сборки документационного сайта:

.. code-block:: bash

   pip install -e ".[docs]"
   cd docs
   sphinx-build -b html . _build/html

Запуск тестов
~~~~~~~~~~~~~

Для запуска модульных тестов библиотеки:

.. code-block:: bash

   pip install -e ".[dev]"
   pytest
