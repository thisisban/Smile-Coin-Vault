from cProfile import label

import flet as ft
import random
import time
import threading
from collections import deque

class ContentContainer:
    def __init__(self):
        self.id = -1
        self.author_name = "Неизв. автор"
        self.topic = "Неизв. тема"
        self.content = "Без существующего контента"


class CurrencyServer:
    def __init__(self):
        self.current_rate = 0.50  # Курс
        self.limit = (0.10, 9999.99)  # Лимит
        self.amplitude = (-0.20, 0.20)  # Амплитуда изменений
        self.lock = threading.Lock()
        self.history = deque(maxlen=6*2)
        self.topics = list()

    def update_rate(self):
        while True:
            with self.lock:
                change = random.uniform(self.amplitude[0], self.amplitude[1])  # Изменение курса
                self.current_rate = max(self.limit[0], min(self.current_rate + change, self.limit[1]))  # Не допускаем значений, заходящих за рамки лимитов
                self.history.append((time.time(), self.current_rate))  # Сохраняем текущее время и курс
            time.sleep(10)

    def get_rate(self):
        with self.lock:
            return self.current_rate

    def get_history(self):
        with self.lock:
            return list(self.history)

    def set_rate(self, new_rate):
        with self.lock:
            self.current_rate = max(self.limit[0], min(new_rate, self.limit[1]))

    def set_amplitude(self, min_amplitude, max_amplitude):
        with self.lock:
            self.amplitude = (min_amplitude, max_amplitude)

    def set_limits(self, min_limit, max_limit):
        with self.lock:
            self.limit = (min_limit, max_limit)

server = CurrencyServer()
threading.Thread(target=server.update_rate, daemon=True).start()

reg_log = ft.TextField(label="Логин")
reg_pass = ft.TextField(label="Пароль", password=True, can_reveal_password=True)

log_log = ft.TextField(label="Логин")
log_pass = ft.TextField(label="Пароль", password=True, can_reveal_password=True)

def main(page: ft.Page):
    page.title = "Хранилище ₲"
    rate_display = ft.Text("1.00", theme_style=ft.TextThemeStyle.TITLE_LARGE)


    if page.client_storage.get("Theme") == None:
        page.client_storage.set("Theme", "1")

    def change_theme(e):
        if e != "s":
            if thm.value == "1":
                page.theme = ft.Theme(color_scheme_seed="#ffc000")
                page.client_storage.set("Theme", "1")
            elif thm.value == "2":
                page.theme = ft.Theme(color_scheme_seed="Green")
                page.client_storage.set("Theme", "2")
            elif thm.value == "3":
                page.theme = ft.Theme(color_scheme_seed="Blue")
                page.client_storage.set("Theme", "3")
            else:
                page.theme = ft.Theme(color_scheme_seed="#ffc000")
                page.client_storage.set("Theme", "1")
            page.update()
        else:
            e = page.client_storage.get("Theme")
            if e == "1":
                page.theme = ft.Theme(color_scheme_seed="#ffc000")
            elif e == "2":
                page.theme = ft.Theme(color_scheme_seed="Green")
            elif e == "3":
                page.theme = ft.Theme(color_scheme_seed="Blue")
            else:
                page.theme = ft.Theme(color_scheme_seed="#ffc000")
            page.update()


    optionsdd = [
        ft.dropdown.Option(key="1", text="Монетная",
                           text_style=ft.TextStyle(#color="#0044cc",
                                                   weight=ft.FontWeight.W_400), ),
        ft.dropdown.Option(key="2", text="Купюрная",
                           text_style=ft.TextStyle(#color="#cc8500",
                                                   weight=ft.FontWeight.W_400)),
        ft.dropdown.Option(key="3", text="Нестрандартно-синяя",
                           text_style=ft.TextStyle(#color="#cc8500",
                                                   weight=ft.FontWeight.W_400)),
    ]

    thm = ft.Dropdown(
        options=optionsdd,
        value=page.client_storage.get("Theme"), on_change=change_theme, label="Тема")

    change_theme("s")

    chart = ft.LineChart(
        data_series=[],
        border=ft.Border(
            bottom=ft.BorderSide(4, ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
        ),
        left_axis=ft.ChartAxis(title=ft.Text("Цена (₽)"), title_size=30, labels_size=70),
        bottom_axis=ft.ChartAxis(title=ft.Text("Время"), title_size=20, labels_size=20),
        tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.GREY),
        expand=False,
        width=600,
        height=310,
        vertical_grid_lines=ft.ChartGridLines(dash_pattern=[5,10], width=0.25, color=ft.colors.BLACK87),
        horizontal_grid_lines=ft.ChartGridLines(dash_pattern=[10,5], width=0.25, color=ft.colors.BLACK87)
    )

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    admin_password = "sc2024v"
    #supervisor_password = "apass"

    def check_admin(e):
        if pfield.value == admin_password:
            page.client_storage.set("admin_password", pfield.value)
            page.go("/admin-panel")
            pfield.error_text = None
        else:
            pfield.error_text = "Неверный пароль"
        pfield.value = ""
        page.update()

    def logout_admin(e):
        page.client_storage.remove("admin_password")
        page.go("/")

    pfield = ft.TextField(label="Пароль", password=True, can_reveal_password=True, on_submit=check_admin, autofocus=True)
    ncourse = ft.TextField(label="Новый курс", value="0.50",
                           on_submit=lambda e: set_new_rate(e.control.value))
    maxamp = ft.TextField(label="Минимальная амплитуда", value="-0.20",
                          on_submit=lambda e: set_min_amplitude(e.control.value))
    minamp = ft.TextField(label="Максимальная амплитуда", value="0.20",
                          on_submit=lambda e: set_max_amplitude(e.control.value))
    minlim = ft.TextField(label="Минимальный лимит", value="0.10",
                          on_submit=lambda e: set_min_limit(e.control.value))
    maxlim = ft.TextField(label="Максимальный лимит", value="9999.99",
                          on_submit=lambda e: set_max_limit(e.control.value))

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.ListTile(
                                        leading=ft.Icon(ft.icons.CURRENCY_BITCOIN),
                                        title=ft.Text("Хранилище SMILE-Коинов"),
                                        subtitle=ft.Text("Главная страница"),
                                        trailing=ft.PopupMenuButton(
                                            icon=ft.icons.MORE_VERT,
                                            items=[
                                                ft.PopupMenuItem(
                                                    text="Настройки", icon=ft.icons.SETTINGS, on_click=lambda e: page.go("/setup")
                                                ),
                                                ft.PopupMenuItem(
                                                    text="Дополнительно", icon=ft.icons.ADMIN_PANEL_SETTINGS, on_click=lambda e: page.go("/admin")
                                                )
                                            ]
                                        )
                                    ),
                                    ft.ListTile(title=ft.Text("Текущий курс ₲"),
                                                subtitle=rate_display),
                                    ft.Divider(),
                                    chart,
                                ]
                            ),
                            width=600,
                            padding=10,
                        )
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.ListTile(
                                        leading=ft.Icon(ft.icons.ANDROID),
                                        title=ft.Text("Больше контента!"),
                                        subtitle=ft.Text("Тут может быть больше контента, если ты напишешь, что добавить в следующем обновлении!"),
                                    ),
                                    ft.Row([
                                        ft.TextButton("Написать", icon=ft.icons.FEEDBACK_OUTLINED, on_click=lambda e: page.go("/openwall")),
                                    ], alignment=ft.MainAxisAlignment.END)
                                ]
                            ),
                            width=600,
                            padding=10,
                        )
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=True,
            )
        )

        if page.route == "/admin":
            if page.client_storage.get("admin_password") == None or page.client_storage.get("admin_password") != admin_password:
                if page.client_storage.get("admin_password") != admin_password and page.client_storage.get("admin_password") != None:
                    pfield.error_text = "Введённый пароль устарел"
                page.views.append(
                    ft.View(
                        "/admin",
                        [
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.SHIELD),
                                                title=ft.Text("Дополнительные инструменты"),
                                                subtitle=ft.Text("Страница защищена паролем"),
                                            ),
                                            pfield,
                                            ft.Row([
                                                ft.TextButton("Назад", on_click=lambda e: page.go("/")),
                                                ft.FilledButton("Войти", on_click=check_admin),
                                            ], alignment=ft.MainAxisAlignment.END)
                                        ]
                                    ),
                                    width=400,
                                    padding=10,
                                )
                            )
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
            else:
                page.go("/admin-panel")
        if page.route == "/admin-panel":
            if page.client_storage.get("admin_password") == admin_password:
                ncourse.value = f"{round(server.current_rate, 2)}"
                maxamp.value = server.amplitude[1]
                minamp.value = server.amplitude[0]
                maxlim.value = server.limit[1]
                minlim.value = server.limit[0]
                page.views.append(
                    ft.View(
                        "/admin-panel",
                        [
                            ft.Column([
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.ListTile(
                                                    leading=ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS),
                                                    title=ft.Text("Дополнительные инструменты"),
                                                    subtitle=ft.Text("Всё, что необходимо для 🤣"),
                                                ),
                                                ft.Row([
                                                    ft.TextButton("Выйти", on_click=logout_admin),
                                                    ft.FilledButton("Закрыть", on_click=lambda e: page.go("/")),
                                                ], alignment=ft.MainAxisAlignment.END)
                                            ]
                                        ),
                                        width=400,
                                        padding=10,
                                    )
                                ),
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.ListTile(
                                                    leading=ft.Icon(ft.icons.BALANCE),
                                                    title=ft.Text("Финансовые изменения"),
                                                    subtitle=ft.Text("🏦 Банк бы оценил"),
                                                ),
                                                ncourse,
                                                maxamp,
                                                minamp,
                                                minlim,
                                                maxlim,
                                                ft.Row([
                                                    ft.FilledButton("Обновить всё", on_click=set_all_new),
                                                ], alignment=ft.MainAxisAlignment.END)
                                            ]
                                        ),
                                        width=400,
                                        padding=10,
                                    )
                                )
                            ])
                        ],
                        scroll=True,
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
            else:
                page.views.append(
                    ft.View(
                        "/admin-panel",
                        [
                            ft.Column([
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.ListTile(
                                                    leading=ft.Icon(ft.icons.ERROR),
                                                    title=ft.Text("Ошибка доступа"),
                                                    subtitle=ft.Text("Необходима авторизация"),
                                                ),
                                                ft.Row([
                                                    ft.FilledButton("Обновить", on_click=lambda e: page.go(page.route)),
                                                    ft.FilledButton("Домой", on_click=lambda e: page.go("/")),
                                                ], alignment=ft.MainAxisAlignment.END)
                                            ]
                                        ),
                                        width=400,
                                        padding=10,
                                    )
                                )
                            ])
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
        if page.route == "/setup":
            page.views.append(
                ft.View(
                    "/setup",
                    [
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.ListTile(
                                            leading=ft.Icon(ft.icons.SETTINGS),
                                            title=ft.Text("Настройки"),
                                            subtitle=ft.Text("Отсюда веет богатством"),
                                        ),
                                        thm,
                                        ft.Row([
                                            ft.TextButton("Назад", on_click=lambda e: page.go("/")),
                                        ], alignment=ft.MainAxisAlignment.END)
                                    ]
                                ),
                                width=400,
                                padding=10,
                            )
                        )
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        if page.route.removeprefix("/openwall") != page.route:
            def create_open_action(topic_id):
                return lambda e: page.go(f"/openwall/view/{topic_id}")

            topic_cards = [
                ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.CHAT_BUBBLE),
                            title=ft.Text(topic.topic),
                            subtitle=ft.Text(f"{topic.author_name}"),
                            trailing=ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        text="Открыть",
                                        icon=ft.icons.OPEN_IN_NEW,
                                        on_click=create_open_action(topic.id)
                                    )
                                ]
                            )
                        ),
                        padding=10,
                        width=600
                    ),
                )
                for topic in server.topics
            ]

            page.views.append(
                ft.View(
                    "/openwall",
                    [
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.ListTile(
                                            leading=ft.Icon(ft.icons.FEEDBACK),
                                            title=ft.Text("Открытая стена"),
                                            subtitle=ft.Text(
                                                "Здесь нужно писать свои идеи, предложения и возможные баги"),
                                        ),
                                        ft.Row([
                                            ft.TextButton("Назад", on_click=lambda e: page.go("/")),
                                        ], alignment=ft.MainAxisAlignment.END),
                                    ],
                                ),
                                width=600,
                                padding=10,
                            ),
                        ),
                        *topic_cards  # Добавляем карточки с топиками
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    floating_action_button=ft.FloatingActionButton(icon=ft.icons.ADD,
                                                                   on_click=lambda e: page.go("/openwall/send"))
                )
            )
        if page.route == "/openwall/send":
            tnamef = ft.TextField(label="Имя", width=300, border=ft.InputBorder.UNDERLINE, filled=True, border_width=2)
            ttopicf = ft.TextField(label="Тема", multiline=True, border=ft.InputBorder.UNDERLINE, filled=True, border_width=2)
            tcontf = ft.TextField(label="Контент", multiline=True, border=ft.InputBorder.UNDERLINE, filled=True, border_width=2)
            def check_topic_vars(e):
                error = False
                tnamev = tnamef.value  # Имя
                ttopicv = ttopicf.value  # Тема
                tcontv = tcontf.value  # Контент

                if not ttopicv:
                    ttopicf.error_text = "Обязательное поле"
                    error = True
                else:
                    ttopicf.error_text = None
                if not tnamev:
                    ttopicf.error_text = "Обязательное поле"
                    error = True
                else:
                    ttopicf.error_text = None
                if not tcontv:
                    tcontf.error_text = "Обязательное поле"
                    error = True
                else:
                    tcontf.error_text = None

                if not error:
                    new_topic = ContentContainer()
                    new_topic.id = str(len(server.topics))
                    new_topic.author_name = tnamev
                    new_topic.topic = ttopicv
                    new_topic.content = tcontv

                    server.topics.insert(0, new_topic)
                    page.go("/openwall")
                else:
                    page.update()




            page.views.append(
                ft.View(
                    "/openwall/send",
                    [
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.ListTile(
                                            leading=ft.Icon(ft.icons.FEEDBACK),
                                            title=ft.Text("Отправка контента"),
                                            subtitle=ft.Text("Напиши всё, что захочешь! Можешь попросить SMILE-Коины, но вряд ли ты их получишь.")
                                        ),
                                        ft.Row([
                                            ft.TextButton("Отмена", on_click=lambda e: page.go("/openwall")),
                                        ], alignment=ft.MainAxisAlignment.END)
                                    ]
                                ),
                                width=600,
                                padding=10,
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        tnamef,
                                        ttopicf,
                                        tcontf,
                                        ft.Row([
                                            ft.FilledButton("Отправить", on_click=check_topic_vars),
                                        ], alignment=ft.MainAxisAlignment.END)
                                    ]
                                ),
                                width=600,
                                padding=10,
                            )
                        )
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        if page.route.removeprefix("/openwall/view/") != page.route:
            print("OK")

            card_id = page.route.removeprefix("/openwall/view/")
            ccard = None

            for i in server.topics:
                if i.id == card_id:
                    ccard = i
                    break

            if ccard:
                page.views.append(
                    ft.View(f"/openwall/view/{page.route.split("/")[3]}",
                        [
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHAT_BUBBLE),
                                                title=ft.Text(ccard.topic),
                                                subtitle=ft.Text(
                                                    ccard.author_name),
                                            ),
                                            ft.Text(ccard.content),
                                            ft.Row([
                                                ft.TextButton("Назад", on_click=lambda e: page.go("/openwall")),
                                            ], alignment=ft.MainAxisAlignment.END),
                                        ],
                                    ),
                                    width=600,
                                    padding=10,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
            else:
                page.views.append(
                    ft.View(
                        f"/openwall/view/{page.route.split("/")[3]}",
                        [
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.NOT_ACCESSIBLE),
                                                title=ft.Text("404"),
                                                subtitle=ft.Text(
                                                    "Тема не найдена среди постов. Возможно, эта тема больше не существует."),
                                            ),
                                            ft.Row([
                                                ft.TextButton("Назад", on_click=lambda e: page.go("/")),
                                            ], alignment=ft.MainAxisAlignment.END),
                                        ],
                                    ),
                                    width=600,
                                    padding=10,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
        page.update()

    def set_all_new(e):
        set_new_rate(False)
        set_min_amplitude(False)
        set_max_amplitude(False)
        set_min_limit(False)
        set_max_limit(False)
        snackbar = ft.SnackBar(ft.Text("Всё обновлено"), open=True)
        page.open(snackbar)
        page.update()

    def set_new_rate(value):
        try:
            if value == False:
                new_rate = float(ncourse.value)
                server.set_rate(new_rate)
                page.update()
            else:
                new_rate = float(value)
                server.set_rate(new_rate)
                snackbar = ft.SnackBar(ft.Text("Курс обновлён!"), open=True)
                page.open(snackbar)
                page.update()
        except ValueError:
            snackbar = ft.SnackBar(ft.Text("Введите корректное значение!"), open=True)
            page.open(snackbar)
            page.update()

    def set_min_amplitude(value):
        try:
            if value == False:
                min_amplitude = float(minamp.value)
                server.set_amplitude(min_amplitude, server.amplitude[1])
                page.update()
            else:
                min_amplitude = float(value)
                server.set_amplitude(min_amplitude, server.amplitude[1])
                snackbar = ft.SnackBar(ft.Text("Минимальная амплитуда обновлена!"), open=True)
                page.open(snackbar)
                page.update()
        except ValueError:
            snackbar = ft.SnackBar(ft.Text("Введите корректное значение!"), open=True)
            page.open(snackbar)
            page.update()

    def set_max_amplitude(value):
        try:
            if value == False:
                max_amplitude = float(maxamp.value)
                server.set_amplitude(server.amplitude[0], max_amplitude)
                page.update()
            else:
                max_amplitude = float(value)
                server.set_amplitude(server.amplitude[0], max_amplitude)
                snackbar = ft.SnackBar(ft.Text("Максимальная амплитуда обновлена!"), open=True)
                page.open(snackbar)
                page.update()
        except ValueError:
            snackbar = ft.SnackBar(ft.Text("Введите корректное значение!"), open=True)
            page.open(snackbar)
            page.update()

    def set_min_limit(value):
        try:
            if value == False:
                min_limit = float(minlim.value)
                server.set_limits(min_limit, server.limit[1])
                page.update()
            else:
                min_limit = float(value)
                server.set_limits(min_limit, server.limit[1])
                snackbar = ft.SnackBar(ft.Text("Минимальный лимит обновлён!"), open=True)
                page.open(snackbar)
                page.update()
        except ValueError:
            snackbar = ft.SnackBar(ft.Text("Введите корректное значение!"), open=True)
            page.open(snackbar)
            page.update()

    def set_max_limit(value):
        try:
            if value == False:
                max_limit = float(maxlim.value)
                server.set_limits(server.limit[0], max_limit)
                page.update()
            else:
                max_limit = float(value)
                server.set_limits(server.limit[0], max_limit)
                snackbar = ft.SnackBar(ft.Text("Максимальный лимит обновлён!"), open=True)
                page.open(snackbar)
                page.update()
        except ValueError:
            snackbar = ft.SnackBar(ft.Text("Введите корректное значение!"), open=True)
            page.open(snackbar)
            page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    def update_display():
        if page.route == "/":
            rate = server.get_rate()
            rate_display.value = f"{rate:.2f}₽"
            page.update()

    def update_chart():
        if page.route == "/":
            history = server.get_history()
            data_points = [
                ft.LineChartDataPoint(
                    x=i * 1,
                    y=rate,
                    tooltip=f"{rate:.2f}"
                ) for i, (_, rate) in enumerate(history)
            ]
            chart.data_series = [
                ft.LineChartData(data_points=data_points, stroke_width=2, color=ft.colors.PRIMARY, curved=False)
            ]

            # Добавление меток на ось Y
            y_labels = sorted(set(rate for _, rate in history))
            chart.left_axis.labels = [ft.ChartAxisLabel(value=rate, label=ft.Text(f"{rate:.2f}")) for rate in y_labels]

            # Добавление меток на ось X
            last_label = None
            chart.bottom_axis.labels = [
                ft.ChartAxisLabel(value=i * 1, label = ft.Text(time.strftime('%H:%M', time.localtime(history[i][0] + 3 * 3600))))
                for i in range(len(history))
                if (label := time.strftime('%H:%M', time.localtime(history[i][0]))) != last_label and (last_label := label)
            ]
            page.update()

    def sync_rate():
        while True:
            if page.route == "/":
                update_display()
                update_chart()
            time.sleep(5)

    threading.Thread(target=sync_rate, daemon=True).start()

ft.app(main, view=ft.AppView.WEB_BROWSER, port=5000, host="0.0.0.0")
