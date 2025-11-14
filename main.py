from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.scrollview import ScrollView
from datetime import datetime
from kivy.uix.image import Image
from kivy.core.window import Window
import json
import os
import shutil


class MyApp(MDApp):
    dialog = None
    notes = []
    current_editing_note = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.current_note_image = None
        self.load_notes()

    def build(self):
        # Theme тохиргоо
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.theme_style = "Light"

        # Фолдер шалгах
        self.ensure_directories()

        # Үндсэн дэлгэц
        self.screen = MDScreen()

        # Top Toolbar
        self.toolbar = MDTopAppBar(
            title="Миний Тэмдэглэл",
            elevation=10,
            pos_hint={'top': 1}
        )
        self.toolbar.right_action_items = [
            ["bell", lambda x: self.show_reminder_dialog()],
            ["download", lambda x: self.show_export_dialog()],
            ["magnify", lambda x: self.show_search_dialog()],
            ["theme-light-dark", lambda x: self.switch_theme()],
            ["plus", lambda x: self.show_note_dialog()]
        ]
        self.screen.add_widget(self.toolbar)

        # Bottom navigation
        self.bottom_nav = MDBottomNavigation(
            panel_color=self.theme_cls.primary_color,
            selected_color_background=self.theme_cls.accent_color,
            text_color_active="white",
        )

        # Нүүр хуудас
        home_tab = MDBottomNavigationItem(
            name='home',
            text='Нүүр',
            icon='home'
        )
        
        # Logo болон нүүр хуудасны агуулга
        home_layout = self.create_home_logo()
        home_tab.add_widget(home_layout)

        # Тэмдэглэлийн хуудас
        notes_tab = MDBottomNavigationItem(
            name='notes',
            text='Тэмдэглэл',
            icon='notebook'
        )

        # Тэмдэглэлийн жагсаалт
        self.notes_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=15,
        )

        # ScrollView + MDList
        scroll = ScrollView()
        self.notes_list = MDList()
        scroll.add_widget(self.notes_list)
        self.notes_layout.add_widget(scroll)

        notes_tab.add_widget(self.notes_layout)

        # Tabs нэмэх
        self.bottom_nav.add_widget(home_tab)
        self.bottom_nav.add_widget(notes_tab)

        self.screen.add_widget(self.bottom_nav)
        self.update_notes_list()

        return self.screen

    def create_home_logo(self):
        """Нүүр хуудасны logo болон мэндчилгээ үүсгэх"""
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=30,
            padding=[20, 50, 20, 20],
            adaptive_height=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Logo хэсэг - Тэмдэглэлийн дүрс
        logo_card = MDCard(
            size_hint=(None, None),
            size=(150, 150),
            pos_hint={'center_x': 0.5},
            elevation=8,
            radius=[75],  # Дугуй хэлбэр
            md_bg_color=self.theme_cls.primary_color
        )
        
        logo_layout = MDBoxLayout(
            orientation='vertical',
            spacing=5,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Notebook icon
        notebook_icon = MDIconButton(
            icon="notebook-outline",
            theme_icon_color="Custom",
            icon_color="white",
            icon_size="60sp",
            pos_hint={'center_x': 0.5}
        )
        
        # Pen icon зураг дээр
        pen_icon = MDIconButton(
            icon="pencil",
            theme_icon_color="Custom", 
            icon_color="white",
            icon_size="30sp",
            pos_hint={'center_x': 0.7, 'center_y': 0.3}
        )
        
        logo_layout.add_widget(notebook_icon)
        logo_card.add_widget(logo_layout)
        logo_card.add_widget(pen_icon)
        
        main_layout.add_widget(logo_card)
        
        # App нэр
        app_name = MDLabel(
            text="Миний Тэмдэглэл",
            font_style="H4",
            theme_text_color="Primary",
            halign="center",
            bold=True
        )
        main_layout.add_widget(app_name)
        
        # Тайлбар текст
        description = MDLabel(
            text="Таны бодол санааг хадгалах\nхамгийн хялбар арга",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(description)
        
        # Мэндчилгээ
        welcome_card = MDCard(
            size_hint_y=None,
            height=80,
            padding=20,
            elevation=2,
            radius=15
        )
        
        welcome_text = MDLabel(
            text="🌟 Тавтай морил! 🌟\nШинэ тэмдэглэл нэмэхийн тулд '+' товчийг дарна уу",
            halign="center",
            theme_text_color="Primary",
            font_style="Body2"
        )
        welcome_card.add_widget(welcome_text)
        main_layout.add_widget(welcome_card)
        
        return main_layout

    def ensure_directories(self):
        """Шаардлагатай фолдерууд үүсгэх"""
        paths = ['images']
        for path in paths:
            full_path = os.path.join(os.getcwd(), path)
            if not os.path.exists(full_path):
                os.makedirs(full_path)

    def switch_theme(self):
        """Theme сольж харагдац солих"""
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def show_note_dialog(self):
        """Шинэ тэмдэглэл нэмэх цонх"""
        self.current_note_image = None

        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="300dp"
        )

        # Гарчиг талбар
        self.title_field = MDTextField(
            hint_text="Гарчиг оруулна уу...",
            size_hint_y=None,
            height=40
        )
        content_layout.add_widget(self.title_field)

        # Текст талбар
        self.note_field = MDTextField(
            multiline=True,
            hint_text="Тэмдэглэлээ бичнэ үү...",
            size_hint_y=None,
            height=100
        )
        content_layout.add_widget(self.note_field)

        # Tag талбар
        self.tag_field = MDTextField(
            hint_text="Tag нэмэх (таслалаар ялгана уу)...",
            size_hint_y=None,
            height=40
        )
        content_layout.add_widget(self.tag_field)

        # Зураг оруулах товч
        image_button = MDFlatButton(
            text="ЗУРАГ НЭМЭХ",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=lambda x: self.file_manager.show('/')
        )
        content_layout.add_widget(image_button)

        # Зургийн нэр
        self.image_label = MDLabel(
            text="",
            theme_text_color="Secondary",
        )
        content_layout.add_widget(self.image_label)

        self.dialog = MDDialog(
            title="Шинэ тэмдэглэл",
            type="custom",
            content_cls=content_layout,
            buttons=[
                MDFlatButton(
                    text="БОЛИХ",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss() # type: ignore
                ),
                MDFlatButton(
                    text="ХАДГАЛАХ",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.save_note()
                ),
            ],
        )
        self.dialog.open()

    def exit_file_manager(self, *args):
        """Файл сонгох цонхыг хаах"""
        self.file_manager.close()

    def select_path(self, path):
        """Зураг сонгосны дараа дуудагдах функц"""
        if os.path.isdir(path):
            self.file_manager.open(path)
        else:
            self.current_note_image = path
            self.image_label.text = f"Сонгосон зураг: {os.path.basename(path)}"
            self.exit_file_manager()

    def save_note(self):
        """Тэмдэглэл хадгалах"""
        if self.note_field.text.strip():
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            image_path = None
            if self.current_note_image:
                ext = os.path.splitext(self.current_note_image)[1]
                image_name = f"image_{current_time}{ext}"
                image_path = os.path.join('images', image_name)
                shutil.copy2(self.current_note_image, image_path)

            # Tag-уудыг боловсруулах
            tags = []
            if self.tag_field.text.strip():
                tags = [tag.strip() for tag in self.tag_field.text.split(',') if tag.strip()]
            
            note = {
                'title': self.title_field.text.strip() or "Гарчиггүй",
                'text': self.note_field.text.strip(),
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'image': image_path,
                'tags': tags
            }

            self.notes.append(note)
            self.save_notes()
            self.update_notes_list()
            self.dialog.dismiss() # type: ignore

    def update_notes_list(self):
        """Тэмдэглэлийн жагсаалтыг шинэчлэх"""
        self.notes_list.clear_widgets()
        for note in reversed(self.notes):
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height="auto",
                padding=15,
                spacing=10,
                elevation=2
            )

            # Гарчиг нэмэх
            title_label = MDLabel(
                text=note.get('title', 'Гарчиггүй'),
                font_style="H6",
                theme_text_color="Primary",
                size_hint_y=None,
                height=30
            )
            card.add_widget(title_label)

            # Tag-ууд харуулах
            if note.get('tags'):
                tags_layout = MDBoxLayout(
                    orientation='horizontal',
                    spacing=5,
                    size_hint_y=None,
                    height=30,
                    adaptive_width=True
                )
                
                for tag in note['tags']:
                    tag_chip = MDCard(
                        size_hint=(None, None),
                        size=(len(tag) * 8 + 20, 25),
                        padding=5,
                        elevation=1,
                        radius=12,
                        md_bg_color=self.theme_cls.accent_color
                    )
                    tag_label = MDLabel(
                        text=f"#{tag}",
                        font_style="Caption",
                        theme_text_color="Custom",
                        text_color="white",
                        halign="center",
                        valign="center"
                    )
                    tag_chip.add_widget(tag_label)
                    tags_layout.add_widget(tag_chip)
                
                card.add_widget(tags_layout)

            text_label = MDLabel(
                text=note['text'],
                size_hint_y=None
            )
            card.add_widget(text_label)

            # Хэрэв зураг байвал нэмэх
            if note.get('image') and os.path.exists(note['image']):
                img = Image(
                    source=note['image'],
                    size_hint_y=None,
                    height=200
                )
                card.add_widget(img)

            date_label = MDLabel(
                text=f"Үүсгэсэн: {note['date']}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height=20
            )
            card.add_widget(date_label)

            # Товчнуудын хэсэг
            button_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=5,
                size_hint_y=None,
                height=40,
                adaptive_width=True
            )
            
            edit_button = MDIconButton(
                icon="pencil",
                theme_text_color="Primary",
                on_release=lambda x, n=note: self.edit_note(n)
            )
            button_layout.add_widget(edit_button)

            delete_button = MDIconButton(
                icon="delete",
                theme_text_color="Error",
                on_release=lambda x, n=note: self.delete_note(n)
            )
            button_layout.add_widget(delete_button)
            
            card.add_widget(button_layout)

            self.notes_list.add_widget(card)

    def delete_note(self, note):
        """Тэмдэглэл устгах"""
        if note.get('image') and os.path.exists(note['image']):
            os.remove(note['image'])
        self.notes.remove(note)
        self.save_notes()
        self.update_notes_list()

    def save_notes(self):
        """Тэмдэглэлүүдийг файлд хадгалах"""
        with open("notes.json", "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False)

    def load_notes(self):
        """Тэмдэглэлүүдийг файлаас унших"""
        try:
            with open("notes.json", "r", encoding="utf-8") as f:
                self.notes = json.load(f)
        except Exception as e:
            print("⚠️ Тэмдэглэл ачаалж чадсангүй:", e)
            self.notes = []

    def show_search_dialog(self):
        """Хайлтын диалог харуулах"""
        self.search_field = MDTextField(
            hint_text="Хайх текст оруулна уу...",
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        
        search_content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=100
        )
        search_content.add_widget(self.search_field)
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="🔍 Тэмдэглэл хайх",
                type="custom",
                content_cls=search_content,
                buttons=[
                    MDFlatButton(
                        text="ЦУЦЛАХ",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog,
                    ),
                    MDFlatButton(
                        text="ХАЙХ",
                        theme_text_color="Custom", 
                        text_color=self.theme_cls.primary_color,
                        on_release=self.search_notes,
                    ),
                ],
            )
        else:
            self.dialog.content_cls = search_content
            self.dialog.title = "🔍 Тэмдэглэл хайх"
        
        self.dialog.open()

    def search_notes(self, instance):
        """Тэмдэглэлүүдээс хайлт хийх"""
        search_text = self.search_field.text.lower().strip()
        
        if not search_text:
            self.update_notes_list()
            self.close_dialog(instance)
            return
            
        # Хайлтын үр дүн
        filtered_notes = []
        for note in self.notes:
            # Текст, гарчиг, огноо, tag-аар хайх
            match_found = (search_text in note['text'].lower() or 
                          search_text in note['title'].lower() or
                          search_text in note['date'].lower())
            
            # Tag-аар хайх
            if not match_found and note.get('tags'):
                for tag in note['tags']:
                    if search_text in tag.lower():
                        match_found = True
                        break
            
            if match_found:
                filtered_notes.append(note)
        
        # Үр дүнг харуулах
        self.display_search_results(filtered_notes, search_text)
        self.close_dialog(instance)

    def display_search_results(self, filtered_notes, search_text):
        """Хайлтын үр дүнг харуулах"""
        self.notes_list.clear_widgets()
        
        if not filtered_notes:
            # Үр дүн олдсонгүй
            no_result_card = MDCard(
                size_hint_y=None,
                height=100,
                padding=20,
                elevation=2,
                radius=10
            )
            no_result_label = MDLabel(
                text=f"'{search_text}' гэсэн хайлтад тохирох тэмдэглэл олдсонгүй",
                halign="center",
                theme_text_color="Secondary"
            )
            no_result_card.add_widget(no_result_label)
            self.notes_list.add_widget(no_result_card)
            
            # Бүх тэмдэглэлийг харуулах товч
            reset_button = MDFlatButton(
                text="Бүх тэмдэглэлийг харуулах",
                on_release=lambda x: self.update_notes_list()
            )
            self.notes_list.add_widget(reset_button)
            return
        
        # Хайлтын үр дүнгийн тоо харуулах
        result_header = MDCard(
            size_hint_y=None,
            height=60,
            padding=15,
            elevation=1,
            radius=5,
            md_bg_color=self.theme_cls.primary_color
        )
        result_text = MDLabel(
            text=f"🔍 '{search_text}' - {len(filtered_notes)} үр дүн олдлоо",
            theme_text_color="Custom",
            text_color="white",
            halign="center",
            font_style="Subtitle1"
        )
        result_header.add_widget(result_text)
        self.notes_list.add_widget(result_header)
        
        # Хайлтын үр дүнг харуулах
        for note in filtered_notes:
            card = MDCard(
                size_hint_y=None,
                height=150,
                padding=10,
                spacing=5,
                elevation=3,
                radius=10,
                orientation='vertical'
            )

            title_label = MDLabel(
                text=note['title'],
                font_style="H6",
                theme_text_color="Primary",
                size_hint_y=None,
                height=30
            )
            card.add_widget(title_label)

            # Хайлтын үгийг онцлох
            highlighted_text = self.highlight_search_text(note['text'], search_text)
            text_label = MDLabel(
                text=highlighted_text[:100] + "..." if len(highlighted_text) > 100 else highlighted_text,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=40
            )
            card.add_widget(text_label)

            if note.get('image') and os.path.exists(note['image']):
                img = Image(
                    source=note['image'],
                    size_hint_y=None,
                    height=80
                )
                card.add_widget(img)

            date_label = MDLabel(
                text=f"Үүсгэсэн: {note['date']}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height=20
            )
            card.add_widget(date_label)

            delete_button = MDIconButton(
                icon="delete",
                theme_text_color="Error",
                on_release=lambda x, n=note: self.delete_note(n)
            )
            card.add_widget(delete_button)

            self.notes_list.add_widget(card)
        
        # Бүх тэмдэглэлийг харуулах товч
        reset_card = MDCard(
            size_hint_y=None,
            height=60,
            padding=10,
            elevation=1,
            radius=5
        )
        reset_button = MDFlatButton(
            text="🔄 Бүх тэмдэглэлийг харуулах",
            on_release=lambda x: self.update_notes_list(),
            pos_hint={'center_x': 0.5}
        )
        reset_card.add_widget(reset_button)
        self.notes_list.add_widget(reset_card)

    def highlight_search_text(self, text, search_text):
        """Хайлтын үгийг онцлох"""
        # Энгийн арга - илүү боловсронгуй болгож болно
        return text

    def edit_note(self, note):
        """Тэмдэглэл засах"""
        self.current_editing_note = note
        
        # Засах диалог үүсгэх
        self.title_field = MDTextField(
            text=note['title'],
            hint_text="Гарчиг",
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        
        self.text_field = MDTextField(
            text=note['text'],
            hint_text="Тэмдэглэл",
            multiline=True,
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        
        # Tag field
        self.edit_tag_field = MDTextField(
            text=', '.join(note.get('tags', [])),
            hint_text="Tag нэмэх (таслалаар ялгана уу)",
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        
        edit_content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=250
        )
        edit_content.add_widget(self.title_field)
        edit_content.add_widget(self.text_field)
        edit_content.add_widget(self.edit_tag_field)
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="✏️ Тэмдэглэл засах",
                type="custom",
                content_cls=edit_content,
                buttons=[
                    MDFlatButton(
                        text="ЦУЦЛАХ",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog,
                    ),
                    MDFlatButton(
                        text="ХАДГАЛАХ",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.save_edited_note,
                    ),
                ],
            )
        else:
            self.dialog.content_cls = edit_content
            self.dialog.title = "✏️ Тэмдэглэл засах"
        
        self.dialog.open()

    def save_edited_note(self, instance):
        """Засагдсан тэмдэглэлийг хадгалах"""
        if self.current_editing_note:
            # Tag-уудыг боловсруулах
            tags = []
            if self.edit_tag_field.text.strip():
                tags = [tag.strip() for tag in self.edit_tag_field.text.split(',') if tag.strip()]
            
            # Мэдээллийг шинэчлэх
            self.current_editing_note['title'] = self.title_field.text
            self.current_editing_note['text'] = self.text_field.text
            self.current_editing_note['tags'] = tags
            self.current_editing_note['date'] = f"Засагдсан: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Хадгалах
            self.save_notes()
            self.update_notes_list()
            self.close_dialog(instance)
            self.current_editing_note = None

    def show_export_dialog(self):
        """Экспорт диалог харуулах"""
        export_content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=100
        )
        
        # Экспорт товчнууд
        txt_button = MDFlatButton(
            text="📄 TXT файл болгон экспорт",
            on_release=lambda x: self.export_notes('txt')
        )
        export_content.add_widget(txt_button)
        
        backup_button = MDFlatButton(
            text="💾 JSON backup үүсгэх",
            on_release=lambda x: self.export_notes('json')
        )
        export_content.add_widget(backup_button)
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="📤 Тэмдэглэлүүдийг экспорт хийх",
                type="custom",
                content_cls=export_content,
                buttons=[
                    MDFlatButton(
                        text="ХААХ",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog,
                    ),
                ],
            )
        else:
            self.dialog.content_cls = export_content
            self.dialog.title = "📤 Тэмдэглэлүүдийг экспорт хийх"
        
        self.dialog.open()

    def export_notes(self, format_type):
        """Тэмдэглэлүүдийг экспорт хийх"""
        if not self.notes:
            self.show_snackbar("Экспорт хийх тэмдэглэл байхгүй байна!")
            self.close_dialog(None)
            return
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'txt':
            filename = f"notes_export_{current_time}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=== МИНИЙ ТЭМДЭГЛЭЛҮҮД ===\n\n")
                    
                    for i, note in enumerate(self.notes, 1):
                        f.write(f"--- Тэмдэглэл #{i} ---\n")
                        f.write(f"Гарчиг: {note.get('title', 'Гарчиггүй')}\n")
                        f.write(f"Огноо: {note['date']}\n")
                        
                        if note.get('tags'):
                            f.write(f"Tag-ууд: {', '.join(note['tags'])}\n")
                        
                        f.write(f"Агуулга:\n{note['text']}\n")
                        
                        if note.get('image'):
                            f.write(f"Зураг: {note['image']}\n")
                        
                        f.write("\n" + "="*50 + "\n\n")
                
                self.show_snackbar(f"✅ {filename} файл амжилттай үүсгэгдлээ!")
                
            except Exception as e:
                self.show_snackbar(f"❌ Алдаа гарлаа: {str(e)}")
        
        elif format_type == 'json':
            filename = f"notes_backup_{current_time}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'export_date': current_time,
                        'total_notes': len(self.notes),
                        'notes': self.notes
                    }, f, ensure_ascii=False, indent=2)
                
                self.show_snackbar(f"✅ {filename} backup файл үүсгэгдлээ!")
                
            except Exception as e:
                self.show_snackbar(f"❌ Алдаа гарлаа: {str(e)}")
        
        self.close_dialog(None)

    def show_snackbar(self, message):
        """Snackbar харуулах"""
        try:
            from kivymd.uix.snackbar import Snackbar
            snackbar = Snackbar(text=message)
            snackbar.open()
        except Exception as e:
            print(f"{message} (Snackbar алдаа: {e})")  # Fallback хэрэв snackbar ажиллахгүй бол

    def show_reminder_dialog(self):
        """Сануулга тохируулах диалог"""
        reminder_content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=200
        )
        
        # Чухал тэмдэглэлүүдийг харуулах
        if self.notes:
            recent_notes = self.notes[-3:]  # Сүүлийн 3 тэмдэглэл
            
            reminder_label = MDLabel(
                text="🔔 Сүүлийн тэмдэглэлүүд:",
                font_style="Subtitle1",
                theme_text_color="Primary",
                size_hint_y=None,
                height=30
            )
            reminder_content.add_widget(reminder_label)
            
            for note in reversed(recent_notes):
                note_summary = MDLabel(
                    text=f"• {note.get('title', 'Гарчиггүй')[:30]}...",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=25
                )
                reminder_content.add_widget(note_summary)
        else:
            no_notes_label = MDLabel(
                text="📝 Одоогоор тэмдэглэл байхгүй байна.\nШинэ тэмдэглэл нэмээрэй!",
                halign="center",
                theme_text_color="Secondary"
            )
            reminder_content.add_widget(no_notes_label)
        
        # Статистик мэдээлэл
        stats_label = MDLabel(
            text=f"📊 Нийт тэмдэглэл: {len(self.notes)}",
            theme_text_color="Primary",
            font_style="Subtitle2",
            size_hint_y=None,
            height=30
        )
        reminder_content.add_widget(stats_label)
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="🔔 Сануулга & Статистик",
                type="custom",
                content_cls=reminder_content,
                buttons=[
                    MDFlatButton(
                        text="ХААХ",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog,
                    ),
                ],
            )
        else:
            self.dialog.content_cls = reminder_content
            self.dialog.title = "🔔 Сануулга & Статистик"
        
        self.dialog.open()


if __name__ == "__main__":
    # Mobile preview хэмжээ
    Window.size = (360, 640)  # Стандарт утасны хэмжээ
    # Window.borderless = True  # Хязгааргүй цонх
    MyApp().run()
