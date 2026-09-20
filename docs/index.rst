Нормативная библиотека строительных материалов
=============================================

Библиотека и интерактивные блокноты для выбора и расчета нормативных и расчетных характеристик строительных материалов в соответствии с актуальными российскими строительными сводами правил.

.. image:: https://img.shields.io/badge/Python-3.9+-blue.svg
   :alt: Python Version
.. image:: https://img.shields.io/badge/СП-63.13330-green.svg
   :alt: СП 63
.. image:: https://img.shields.io/badge/СП-16.13330-orange.svg
   :alt: СП 16
.. image:: https://img.shields.io/badge/СП-15.13330-red.svg
   :alt: СП 15

Поддерживаемые нормативные документы:

* **СП 63.13330.2018** «Бетонные и железобетонные конструкции» (тяжелый, мелкозернистый, легкий, поризованный, ячеистый, напрягающий бетон; арматура А240–А1000, В500, К1500; деформационные диаграммы).
* **СП 16.13330.2017** «Стальные конструкции» (фасонный прокат по ГОСТ 27772, двутавры по ГОСТ Р 57837, листовой прокат; коэффициенты условий работы :math:`\gamma_c`; болты 5.6–12.9; диаграммы вариантов OBD, OACD, OACDEF).
* **СП 15.13330.2020** «Каменные и армокаменные конструкции» (каталоги таблиц 6.1–6.18, кладка из кирпича, блоков и камней; сетчатое армирование по формуле 7.23; упругие характеристики).

Быстрый пример
--------------

.. code-block:: python

   from structural_materials import Concrete, Rebar, StructuralSteel, SteelBolt, Masonry

   # Бетон B25 и арматура A500 (СП 63)
   concrete = Concrete(grade='B25', humidity='40-75%', long_term=True)
   rebar = Rebar(grade='A500')
   print(f"Бетон B25: Rb = {concrete.Rb} МПа, Eb,red = {concrete.Eb_red} МПа")
   print(f"Арматура A500: Rs = {rebar.Rs} МПа")

   # Фасонный прокат С255 и болт 8.8 (СП 16)
   steel = StructuralSteel(grade='С255', profile_type='shapes', thickness=14.0, statistical_control=True)
   bolt = SteelBolt(grade='8.8', diameter=20, gamma_b=0.9)
   print(f"Сталь С255 (tf=14 мм): Ry = {steel.Ry} МПа, Ru = {steel.Ru} МПа")
   print(f"Болт 8.8 М20: срез Nbs = {bolt.shear_capacity(1):.1f} кН, растяжение Nbt = {bolt.tension_capacity():.1f} кН")

   # Кирпичная кладка М150 / М100 (СП 15)
   masonry = Masonry('brick', 'M150', 'M100')
   reinforced = masonry.with_mesh_reinforcement(d=4, s=50, c=2, s_vert=65)
   print(f"Кладка: R = {masonry.R:.2f} МПа, Rsk = {reinforced.Rsk:.2f} МПа")

Интерактивные блокноты
----------------------

Для быстрого подбора материалов и визуализации доступны онлайн-витрины блокнотов:

* `Селектор стали и болтов (СП 16) <https://jupyter.propgs.ru/localfile/materials/steel_selector.ipynb>`_
* `Селектор бетона и арматуры (СП 63) <https://jupyter.propgs.ru/localfile/materials/beton_armatura_selector.ipynb>`_
* `Селектор каменной кладки (СП 15) <https://jupyter.propgs.ru/localfile/materials/masonry_selector.ipynb>`_

Содержание
----------

.. toctree::
   :maxdepth: 2

   installation
   sp63
   sp16
   sp15
   api
