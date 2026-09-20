"""Generate the SP 63 material-selector notebook."""

import json
import hashlib
import textwrap
from pathlib import Path


def _markdown(source: str) -> dict:
    source = textwrap.dedent(source).lstrip()
    return {
        "cell_type": "markdown",
        "id": hashlib.sha1(("markdown\0" + source).encode("utf-8")).hexdigest()[:8],
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def _code(source: str) -> dict:
    source = textwrap.dedent(source).lstrip()
    return {
        "cell_type": "code",
        "id": hashlib.sha1(("code\0" + source).encode("utf-8")).hexdigest()[:8],
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def create_notebook(output_path: Path | None = None) -> Path:
    """Write the SP 63 notebook beside this generator or to ``output_path``."""

    cells = [
        _markdown(
            r"""
            # Интерактивный селектор материалов по СП 63.13330.2018

            Блокнот показывает нормативные характеристики бетона и арматуры,
            а также диаграммы деформирования по СП 63.13330.2018. Точки на
            графиках берутся из API `get_diagram_points`, поэтому подписи всегда
            соответствуют выбранной модели и состоянию материала.
            """
        ),
        _code(
            r'''
            import sys
            from pathlib import Path

            import matplotlib.pyplot as plt
            import numpy as np
            import ipywidgets as widgets
            from IPython.display import HTML, Markdown, clear_output, display

            project_dir = Path.cwd()
            for p in [project_dir, project_dir.parent, project_dir.parent / "structural_materials"]:
                if str(p) not in sys.path:
                    sys.path.insert(0, str(p))

            from sp63_materials import (
                Concrete,
                Rebar,
                list_concrete_grades,
                list_rebar_grades,
            )

            print("Модуль sp63_materials успешно загружен.")
            '''
        ),
        _markdown(
            """
            ## Интерактивный выбор

            Сжатие отображается отрицательными деформациями и напряжениями,
            растяжение — положительными. Для каждой кривой подписываются именно
            те узлы, которые возвращает выбранная нормативная модель.
            """
        ),
        _code(
            r'''
            w_concrete_type = widgets.Dropdown(
                options=[
                    ("Тяжелый", "heavy"),
                    ("Мелкозернистый", "fine_grained"),
                    ("Легкий", "light"),
                    ("Поризованный", "porous"),
                    ("Ячеистый", "cellular"),
                    ("Напрягающий", "tensioning"),
                ],
                value="heavy",
                description="Вид бетона:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="98%"),
            )
            w_concrete_grade = widgets.Dropdown(
                options=list_concrete_grades(),
                value="B25",
                description="Класс бетона:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="98%"),
            )
            w_humidity = widgets.Dropdown(
                options=[
                    ("Сухая (< 40 %)", "<40%"),
                    ("Нормальная (40–75 %)", "40-75%"),
                    ("Повышенная (> 75 %)", ">75%"),
                ],
                value="40-75%",
                description="Влажность среды:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="98%"),
            )
            w_density = widgets.BoundedFloatText(
                value=2400.0,
                min=1.0,
                max=4000.0,
                description="Плотность, кг/м³:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="98%"),
            )
            w_cellular_humidity = widgets.FloatSlider(
                value=25.0,
                min=0.0,
                max=100.0,
                step=1.0,
                description="Влажность ячеистого, %:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="98%"),
            )
            w_curing = widgets.Dropdown(
                options=[("Естественное", None), ("Тепловлажностное", "steam")],
                value=None,
                description="Условия твердения:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="98%"),
            )
            w_long_term = widgets.Checkbox(
                value=True,
                description="Длительное действие нагрузки",
                indent=False,
            )
            w_gamma_b2 = widgets.FloatSlider(
                value=1.0, min=0.1, max=1.0, step=0.01,
                description="γb2:", style={"description_width": "150px"},
            )
            w_gamma_b3 = widgets.FloatSlider(
                value=1.0, min=0.1, max=1.0, step=0.01,
                description="γb3:", style={"description_width": "150px"},
            )
            w_gamma_b4 = widgets.FloatSlider(
                value=1.0, min=0.1, max=1.0, step=0.01,
                description="γb4:", style={"description_width": "150px"},
            )
            w_gamma_b5 = widgets.FloatSlider(
                value=1.0, min=0.1, max=1.0, step=0.01,
                description="γb5:", style={"description_width": "150px"},
            )
            w_diag_model = widgets.RadioButtons(
                options=[
                    ("Двухлинейная, 6.1.21", "bilinear"),
                    ("Трехлинейная, 6.1.20", "trilinear"),
                    ("Нелинейная, приложение Г", "nonlinear"),
                ],
                value="nonlinear",
                description="Модель бетона:",
                style={"description_width": "150px"},
            )
            w_rebar_grade = widgets.Dropdown(
                options=list_rebar_grades(),
                value="A500",
                description="Класс арматуры:",
                style={"description_width": "150px"},
            )
            w_rebar_model = widgets.Dropdown(
                options=[
                    ("Автоматически по 6.2.13", "auto"),
                    ("Двухлинейная", "bilinear"),
                    ("Трехлинейная", "trilinear"),
                ],
                value="auto",
                description="Модель арматуры:",
                style={"description_width": "150px"},
            )
            out_panel = widgets.Output()


            def _set_limits(axis, eps):
                low, high = float(np.min(eps)), float(np.max(eps))
                span = max(high - low, 1e-6)
                axis.set_xlim(low - 0.08 * span, high + 0.08 * span)


            def _plot_named_points(axis, points, color):
                for index, (label, (epsilon, sigma)) in enumerate(points.items()):
                    x_value = epsilon * 1000.0
                    axis.scatter([x_value], [sigma], color=color, s=26, zorder=5)
                    offset = (6, 8 if index % 2 == 0 else -16)
                    axis.annotate(
                        label,
                        xy=(x_value, sigma),
                        xytext=offset,
                        textcoords="offset points",
                        fontsize=8,
                        color=color,
                        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8},
                    )


            def _concrete_diagram(concrete, state):
                selected_model = w_diag_model.value
                if selected_model == "nonlinear":
                    eps, sig = concrete.get_diagram(
                        model="nonlinear", state=state, n_points=160, signed=True
                    )
                    points = concrete.get_diagram_points(
                        model="nonlinear", state=state, signed=True
                    )
                else:
                    eps, sig = concrete.get_diagram(
                        model=selected_model, state=state, n_points=160, signed=True
                    )
                    points = concrete.get_diagram_points(
                        model=selected_model, state=state, signed=True
                    )
                return eps, sig, points


            def update_view(*_):
                with out_panel:
                    clear_output(wait=True)
                    try:
                        concrete = Concrete(
                            grade=w_concrete_grade.value,
                            concrete_type=w_concrete_type.value,
                            humidity=w_humidity.value,
                            long_term=w_long_term.value,
                            gamma_b2=w_gamma_b2.value,
                            gamma_b3=w_gamma_b3.value,
                            gamma_b4=w_gamma_b4.value,
                            gamma_b5=w_gamma_b5.value,
                            density=w_density.value,
                            curing=w_curing.value,
                            cellular_humidity_percent=w_cellular_humidity.value,
                        )
                        rebar = Rebar(
                            grade=w_rebar_grade.value,
                            long_term=w_long_term.value,
                        )
                        eps_c, sig_c, points_c = _concrete_diagram(concrete, "compression")
                        eps_t, sig_t, points_t = _concrete_diagram(concrete, "tension")
                        eps_s, sig_s = rebar.get_diagram(
                            model=w_rebar_model.value,
                            state="tension",
                            n_points=160,
                            signed=True,
                        )
                        points_s = rebar.get_diagram_points(
                            model=w_rebar_model.value, state="tension", signed=True
                        )
                    except ValueError as error:
                        display(Markdown(f"**Параметры требуют уточнения:** `{error}`"))
                        return

                    fig, (ax_c, ax_t, ax_s) = plt.subplots(
                        1, 3, figsize=(17, 5.2), dpi=110, constrained_layout=True
                    )
                    ax_c.plot(eps_c * 1000.0, sig_c, color="#1f77b4", lw=2.2)
                    _plot_named_points(ax_c, points_c, "#d62728")
                    ax_c.set_title(f"Бетон {concrete.grade}: сжатие")
                    ax_c.set_xlabel("ε, ‰ (укорочение со знаком −)")
                    ax_c.set_ylabel("σ, МПа")
                    _set_limits(ax_c, eps_c * 1000.0)

                    ax_t.plot(eps_t * 1000.0, sig_t, color="#2ca02c", lw=2.2)
                    _plot_named_points(ax_t, points_t, "#d62728")
                    ax_t.set_title(f"Бетон {concrete.grade}: растяжение")
                    ax_t.set_xlabel("ε, ‰ (удлинение со знаком +)")
                    ax_t.set_ylabel("σ, МПа")
                    _set_limits(ax_t, eps_t * 1000.0)

                    ax_s.plot(eps_s * 1000.0, sig_s, color="#ff7f0e", lw=2.2)
                    _plot_named_points(ax_s, points_s, "#9467bd")
                    ax_s.set_title(f"Арматура {rebar.grade}: {w_rebar_model.value}")
                    ax_s.set_xlabel("ε, ‰")
                    ax_s.set_ylabel("σ, МПа")
                    _set_limits(ax_s, eps_s * 1000.0)

                    for axis in (ax_c, ax_t, ax_s):
                        axis.grid(True, linestyle=":", alpha=0.6)
                        axis.axhline(0.0, color="black", lw=0.7, alpha=0.5)
                        axis.axvline(0.0, color="black", lw=0.7, alpha=0.5)
                    plt.show()

                    display(HTML(concrete.to_html()))
                    display(HTML(rebar.to_html()))


            controls = [
                w_concrete_type, w_concrete_grade, w_humidity, w_density,
                w_cellular_humidity, w_curing, w_long_term, w_gamma_b2,
                w_gamma_b3, w_gamma_b4, w_gamma_b5, w_diag_model,
                w_rebar_grade, w_rebar_model,
            ]
            for widget in controls:
                widget.observe(update_view, names="value")

            concrete_box = widgets.VBox(
                [
                    widgets.HTML("<b>Параметры бетона</b>"),
                    w_concrete_type, w_concrete_grade, w_humidity, w_density,
                    w_cellular_humidity, w_curing, w_long_term,
                    w_gamma_b2, w_gamma_b3, w_gamma_b4, w_gamma_b5, w_diag_model,
                ],
                layout=widgets.Layout(border="1px solid #ddd", padding="10px"),
            )
            rebar_box = widgets.VBox(
                [widgets.HTML("<b>Параметры арматуры</b>"), w_rebar_grade, w_rebar_model],
                layout=widgets.Layout(border="1px solid #ddd", padding="10px"),
            )
            display(widgets.HBox([concrete_box, rebar_box]))
            display(out_panel)
            update_view()
            '''
        ),
        _markdown(
            """
            ## Пример прямого использования

            Этот пример можно скопировать в расчетный скрипт без виджетов.
            """
        ),
        _code(
            r'''
            # Статический рендер по умолчанию: сохраняется и при nbconvert,
            # даже если интерактивные Output-виджеты не сериализуются.
            demo_concrete = Concrete("B25", long_term=True)
            demo_rebar = Rebar("A500")
            demo_fig, demo_axes = plt.subplots(
                1, 3, figsize=(17, 5.2), dpi=110, constrained_layout=True
            )
            for axis, state, title, color in [
                (demo_axes[0], "compression", "Бетон B25: сжатие", "#1f77b4"),
                (demo_axes[1], "tension", "Бетон B25: растяжение", "#2ca02c"),
            ]:
                eps, sig = demo_concrete.get_diagram(
                    model="nonlinear", state=state, n_points=160, signed=True
                )
                points = demo_concrete.get_diagram_points(
                    model="nonlinear", state=state, signed=True
                )
                axis.plot(eps * 1000.0, sig, color=color, lw=2.2)
                _plot_named_points(axis, points, "#d62728")
                axis.set_title(title)
                axis.set_xlabel("ε, ‰")
                axis.set_ylabel("σ, МПа")
                axis.grid(True, linestyle=":", alpha=0.6)
                axis.axhline(0.0, color="black", lw=0.7, alpha=0.5)
                axis.axvline(0.0, color="black", lw=0.7, alpha=0.5)
                _set_limits(axis, eps * 1000.0)
            eps, sig = demo_rebar.get_diagram(
                model="auto", state="tension", n_points=160, signed=True
            )
            points = demo_rebar.get_diagram_points(
                model="auto", state="tension", signed=True
            )
            demo_axes[2].plot(eps * 1000.0, sig, color="#ff7f0e", lw=2.2)
            _plot_named_points(demo_axes[2], points, "#9467bd")
            demo_axes[2].set_title("Арматура A500: auto")
            demo_axes[2].set_xlabel("ε, ‰")
            demo_axes[2].set_ylabel("σ, МПа")
            demo_axes[2].grid(True, linestyle=":", alpha=0.6)
            demo_axes[2].axhline(0.0, color="black", lw=0.7, alpha=0.5)
            demo_axes[2].axvline(0.0, color="black", lw=0.7, alpha=0.5)
            _set_limits(demo_axes[2], eps * 1000.0)
            plt.show()
            display(HTML(demo_concrete.to_html()))
            display(HTML(demo_rebar.to_html()))
            '''
        ),
        _code(
            r'''
            concrete_example = Concrete("B25", long_term=True)
            rebar_example = Rebar("A500")
            b = 300.0       # ширина сечения, мм
            h = 600.0       # высота сечения, мм
            a = 40.0        # защитный слой до центра арматуры, мм
            h0 = h - a
            As = 3.0 * np.pi * 25.0**2 / 4.0
            x = rebar_example.Rs * As / (concrete_example.Rb * b)
            moment = concrete_example.Rb * b * x * (h0 - 0.5 * x) / 1e6
            print(f"x = {x:.1f} мм; M = {moment:.2f} кН·м")
            '''
        ),
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.13"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    target = Path(output_path) if output_path is not None else Path(__file__).resolve().parent.parent / "notebooks" / "material_selector.ipynb"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    print(f"Created notebook at {create_notebook()}")
