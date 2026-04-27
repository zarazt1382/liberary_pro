import tkinter as tk
from tkinter import ttk, messagebox, font
import jdatetime
import json
import os
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from telegram_bot import * 

print("Start...")

class ModernButton(tk.Button):
    """کلاس دکمه مدرن بدون hover"""
    def __init__(self, parent, **kwargs):
        
        self.bg_color = kwargs.pop('bg', '#4361ee')
        self.fg_color = kwargs.pop('fg', 'white')
        self.active_bg = kwargs.pop('activebackground', '#3a56d4')
        self.active_fg = kwargs.pop('activeforeground', 'white')
        
        super().__init__(parent, 
                        bg=self.bg_color,
                        fg=self.fg_color,
                        activebackground=self.active_bg,
                        activeforeground=self.active_fg,
                        relief=tk.RAISED,
                        borderwidth=2,
                        cursor='hand2',
                        **kwargs)

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 سیستم مدیریت کتابخانه - پنل کاربر")
        self.root.geometry("1400x900")
        
        
        self.root.resizable(True,True)
        
        self.setup_theme()

        self.data_file = "library_data_fa.json"
        self.users_data_file = "library_users_fa.json"
        self.email_config_file = "email_config.json"
        self.telegram_config_file = "telegram_config.json"
        
        self.email_config = self.load_email_config()
        self.telegram_config = self.load_telegram_config()

        self.books = []
        self.users = []
        self.load_data()
        self.migrate_old_data()

        self.setup_styles()
        self.setup_gui()

    def setup_styles(self):
        """تنظیم استایل‌های پیشرفته"""
        self.style = ttk.Style()
        
        # استایل Treeview
        self.style.configure("Custom.Treeview",
                            background="white",
                            foreground="black",
                            rowheight=30,
                            fieldbackground="white",
                            font=('Tahoma', 10))
            
        self.style.configure("Custom.Treeview.Heading",
                            background='#4361ee',
                            foreground='white',
                            relief='flat',
                            font=('Tahoma', 11, 'bold'),
                            padding=(10, 5))
        
        self.style.map("Custom.Treeview.Heading",
                        background=[('active', '#3a56d4')])

    def setup_theme(self):
        self.colors = {
            'primary': '#4361ee',
            'primary_dark': '#3a56d4',
            'secondary': '#7209b7',
            'danger': '#e63946',
            'success': '#2a9d8f',
            'warning': '#e9c46a',
            'info': '#4895ef',
            'light': '#f8f9fa',
            'dark': '#212529',
            'gray': '#adb5bd',
            'bg_light': '#f1faee',
            'entry_normal': '#ffffff',
            'entry_focus': '#e3f2fd',
            'panel_bg': '#ffffff',
            'border': '#dee2e6'
        }
        
        self.fonts = {
            'header': ('Tahoma', 16, 'bold'),
            'subheader': ('Tahoma', 12, 'bold'),
            'normal': ('Tahoma', 10),
            'small': ('Tahoma', 9),
            'button': ('Tahoma', 10, 'bold')
        }

    def load_email_config(self):
        default_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': '',
            'enable_tls': True
        }
        
        if os.path.exists(self.email_config_file):
            try:
                with open(self.email_config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config

    def load_telegram_config(self):
        default_config = {
            'bot_token': '',
            'chat_id': '',
            'enable_telegram': True
        }
        
        if os.path.exists(self.telegram_config_file):
            try:
                with open(self.telegram_config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config

    def create_panel(self, parent, title, row, column, columnspan=1):
        """ایجاد پنل مدرن"""
        panel = tk.Frame(parent, 
                        bg=self.colors['panel_bg'],
                        relief=tk.RAISED,
                        borderwidth=2,
                        padx=10,
                        pady=10)
        panel.grid(row=row, column=column, columnspan=columnspan,
                    sticky=(tk.W, tk.E, tk.N, tk.S),
                    padx=8, pady=8)
        
        # عنوان پنل
        title_frame = tk.Frame(panel, bg=self.colors['primary'], height=40)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                                text=title,
                                font=self.fonts['subheader'],
                                bg=self.colors['primary'],
                                fg='white',
                                padx=10)
        title_label.pack(expand=True, fill=tk.BOTH, anchor='center')
        
        return panel

    def setup_gui(self):
        self.root.configure(bg=self.colors['bg_light'])
        
        # هدر اصلی
        header_frame = tk.Frame(self.root, 
                                bg=self.colors['primary'],
                                height=100)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                                text="📚 سیستم مدیریت کتابخانه دانشگاه",
                                font=('Tahoma', 22, 'bold'),
                                bg=self.colors['primary'],
                                fg='white',
                                pady=10)
        header_label.pack(expand=True)
        
        sub_label = tk.Label(header_frame,
                            text="پنل مدیریت کتاب‌ها و کاربران",
                            font=('Tahoma', 12),
                            bg=self.colors['primary'],
                            fg='#e9ecef')
        sub_label.pack()
        
        # کانتینر اصلی با اسکرول
        main_container = tk.Frame(self.root, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # ایجاد Canvas برای اسکرول
        self.canvas = tk.Canvas(main_container, 
                                bg=self.colors['bg_light'], 
                                highlightthickness=0)
        
        scrollbar_y = ttk.Scrollbar(main_container, 
                                    orient=tk.VERTICAL, 
                                    command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_container, 
                                    orient=tk.HORIZONTAL, 
                                    command=self.canvas.xview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_light'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), 
                                    window=self.scrollable_frame, 
                                    anchor="nw")
        
        self.canvas.configure(yscrollcommand=scrollbar_y.set,
                                xscrollcommand=scrollbar_x.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.bind_mouse_scroll_all()
        
        # کانتینر پنل‌ها
        panels_container = tk.Frame(self.scrollable_frame, bg=self.colors['bg_light'])
        panels_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # تنظیم grid برای پنل‌ها
        panels_container.columnconfigure(0, weight=1)
        panels_container.columnconfigure(1, weight=1)
        panels_container.columnconfigure(2, weight=1)
        panels_container.rowconfigure(0, weight=1)
        panels_container.rowconfigure(1, weight=1)
        
        # ایجاد پنل‌ها
        self.right_panel = self.create_panel(panels_container, "📖 مدیریت کتاب‌ها", 0, 0)
        self.setup_right_panel()
        
        self.middle_panel = self.create_panel(panels_container, "👥 مدیریت کاربران", 0, 1)
        self.setup_middle_panel()
        
        self.left_panel = self.create_panel(panels_container, "⚙️ عملیات و گزارش", 0, 2)
        self.setup_left_panel()
        
        self.bottom_panel = self.create_panel(panels_container, "🗑️ مدیریت سوابق", 1, 0, columnspan=3)
        self.setup_bottom_panel()

        # بارگذاری اولیه داده‌ها
        self.update_display()
        self.update_stats()
        self.update_users_display()
        self.clear_date_fields()
        self.clear_selection()
        self.current_user = None
        
        # بررسی خودکار کتاب‌های معوق
        self.root.after(1000, self.check_overdue_books)

    def setup_right_panel(self):
        """تنظیم پنل راست - مدیریت کتاب‌ها"""
        content_frame = tk.Frame(self.right_panel, 
                                bg=self.colors['panel_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # بخش جستجو
        search_container = tk.Frame(content_frame, bg=self.colors['panel_bg'])
        search_container.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_container,
                text="جستجوی کتاب:",
                font=self.fonts['normal'],
                bg=self.colors['panel_bg'],
                fg=self.colors['dark']).pack(side=tk.RIGHT, padx=(0, 10))
        
        self.search_entry = tk.Entry(search_container,
                                    font=self.fonts['normal'],
                                    bg='white',
                                    fg='black',
                                    relief=tk.SOLID,
                                    borderwidth=1,
                                    width=35,
                                    justify='right')
        self.search_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        self.search_entry.bind('<KeyRelease>', self.search_books)
        
        # Treeview کتاب‌ها
        tree_container = tk.Frame(content_frame, 
                                bg=self.colors['panel_bg'])
        tree_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ایجاد Treeview با استایل سفارشی
        self.tree = ttk.Treeview(tree_container,
                                style="Custom.Treeview",
                                columns=('عنوان', 'نویسنده', 'سال', 'موجودی', 'وضعیت'),
                                show='headings',
                                height=10)
        
        headings = [
            ('عنوان', 200),
            ('نویسنده', 170),
            ('سال', 80),
            ('موجودی', 50),
            ('وضعیت', 100)
        ]
        
        for col, width in headings:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=width, minwidth=width, anchor='center', stretch=False)
        
        # نوارهای اسکرول عمودی و افقی
        tree_scrollbar_y = ttk.Scrollbar(tree_container,
                                        orient=tk.VERTICAL,
                                        command=self.tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_container,
                                        orient=tk.HORIZONTAL,
                                        command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=tree_scrollbar_y.set,
                            xscrollcommand=tree_scrollbar_x.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_book_select)
        
        # دکمه‌های عملیاتی
        button_frame = tk.Frame(content_frame, bg=self.colors['panel_bg'])
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        buttons_config = [
            ("🗑️ پاک کردن", self.clear_selection, self.colors['gray']),
            ("↪️ برگشت", self.return_book, self.colors['success']),
            ("📥 امانت", self.borrow_book_dialog, self.colors['primary'])
        ]
        
        for text, command, color in reversed(buttons_config):
            btn = tk.Button(button_frame,
                        text=text,
                        command=command,
                        font=self.fonts['small'],
                        bg=color,
                        fg='white',
                        relief=tk.RAISED,
                        borderwidth=1,
                        padx=10,
                        pady=3,
                        cursor='hand2')
            btn.pack(side=tk.RIGHT, padx=5, pady=2)

    def setup_middle_panel(self):
        """تنظیم پنل وسط - مدیریت کاربران"""
        content_frame = tk.Frame(self.middle_panel, 
                                bg=self.colors['panel_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # فرم ثبت کاربر جدید
        user_form_frame = tk.Frame(content_frame,
                                bg=self.colors['panel_bg'],
                                relief=tk.SOLID,
                                borderwidth=1,
                                padx=15,
                                pady=15)
        user_form_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(user_form_frame,
                text="➕ ثبت کاربر جدید",
                font=self.fonts['subheader'],
                bg=self.colors['panel_bg'],
                fg=self.colors['primary']).pack(anchor='center', pady=(0, 10))
        
        # فیلدهای ورودی
        fields = [
            ("نام:", "first_name_entry"),
            ("نام خانوادگی:", "last_name_entry"),
            ("شماره تماس:", "phone_entry"),
            ("شماره دانشجویی:", "student_id_entry"),
            ("ایمیل:", "email_entry")
        ]
        
        for label_text, attr_name in fields:
            row_frame = tk.Frame(user_form_frame, bg=self.colors['panel_bg'])
            row_frame.pack(fill=tk.X, pady=3)
            
            tk.Label(row_frame,
                    text=label_text,
                    font=self.fonts['small'],
                    bg=self.colors['panel_bg'],
                    fg=self.colors['dark'],
                    anchor='e',
                    width=15).pack(side=tk.RIGHT, padx=(10, 5))
            
            entry = tk.Entry(row_frame,
                        font=self.fonts['small'],
                        bg='white',
                        fg='black',
                        relief=tk.SOLID,
                        borderwidth=1,
                        justify='right')
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=3)
            setattr(self, attr_name, entry)
        
        # دکمه‌های فرم
        form_buttons_frame = tk.Frame(user_form_frame, bg=self.colors['panel_bg'])
        form_buttons_frame.pack(fill=tk.X, pady=(15, 5))
        
        tk.Button(form_buttons_frame,
                text="🗑️ پاک کردن",
                command=self.clear_user_info,
                font=self.fonts['small'],
                bg=self.colors['warning'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=1,
                padx=15,
                pady=3,
                cursor='hand2').pack(side=tk.RIGHT, padx=5)
        
        tk.Button(form_buttons_frame,
                text="💾 ذخیره کاربر",
                command=self.save_user_info,
                font=self.fonts['small'],
                bg=self.colors['success'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=1,
                padx=15,
                pady=3,
                cursor='hand2').pack(side=tk.RIGHT)
        
        # لیست کاربران
        users_list_frame = tk.Frame(content_frame,
                                bg=self.colors['panel_bg'])
        users_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(users_list_frame,
                text="👥 کاربران ثبت‌شده",
                font=self.fonts['subheader'],
                bg=self.colors['panel_bg'],
                fg=self.colors['primary']).pack(anchor='center', pady=(0, 5))
        
        # Treeview کاربران با اسکرول افقی
        users_tree_container = tk.Frame(users_list_frame,
                                    bg=self.colors['panel_bg'])
        users_tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.users_tree = ttk.Treeview(users_tree_container,
                                    style="Custom.Treeview",
                                    columns=('نام', 'نام خانوادگی', 'شماره دانشجویی', 'تلفن', 'ایمیل'),
                                    show='headings',
                                    height=6)
        
        user_columns = [
            ('نام', 100),
            ('نام خانوادگی', 100),
            ('شماره دانشجویی', 100),
            ('تلفن', 100),
            ('ایمیل', 100)
        ]
        
        for col, width in user_columns:
            self.users_tree.heading(col, text=col, anchor='center')
            self.users_tree.column(col, width=width, minwidth=width, anchor='center', stretch=False)
        
        # اسکرول‌بارهای عمودی و افقی
        users_scrollbar_y = ttk.Scrollbar(users_tree_container,
                                        orient=tk.VERTICAL,
                                        command=self.users_tree.yview)
        users_scrollbar_x = ttk.Scrollbar(users_tree_container,
                                        orient=tk.HORIZONTAL,
                                        command=self.users_tree.xview)
        
        self.users_tree.configure(yscrollcommand=users_scrollbar_y.set,
                                xscrollcommand=users_scrollbar_x.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        users_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # دکمه‌های مدیریت کاربران
        user_actions_frame = tk.Frame(users_list_frame, bg=self.colors['panel_bg'])
        user_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(user_actions_frame,
                text="✅ انتخاب",
                command=self.select_user_from_list,
                font=self.fonts['small'],
                bg=self.colors['info'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=1,
                padx=15,
                pady=3,
                cursor='hand2').pack(side=tk.RIGHT, padx=5)
        
        tk.Button(user_actions_frame,
                text="🗑️ حذف",
                command=self.delete_selected_user,
                font=self.fonts['small'],
                bg=self.colors['danger'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=1,
                padx=15,
                pady=3,
                cursor='hand2').pack(side=tk.RIGHT)
        
        # نمایش کاربر فعلی
        current_user_frame = tk.Frame(content_frame,
                                    bg=self.colors['panel_bg'],
                                    relief=tk.SOLID,
                                    borderwidth=1,
                                    padx=10,
                                    pady=10)
        current_user_frame.pack(fill=tk.X)
        
        tk.Label(current_user_frame,
                text="👤 کاربر فعلی:",
                font=self.fonts['small'],
                bg=self.colors['panel_bg'],
                fg=self.colors['dark']).pack(side=tk.RIGHT, padx=(0, 10))
        
        self.current_user_label = tk.Label(current_user_frame,
                                        text="هیچ کاربری انتخاب نشده",
                                        font=self.fonts['small'],
                                        bg=self.colors['panel_bg'],
                                        fg=self.colors['primary'],
                                        anchor='w')
        self.current_user_label.pack(side=tk.RIGHT, expand=True, fill=tk.X)

    def setup_left_panel(self):
        """تنظیم پنل چپ - عملیات و گزارش"""
        content_frame = tk.Frame(self.left_panel,
                                bg=self.colors['panel_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # اطلاعات کتاب انتخاب‌شده
        book_info_frame = tk.Frame(content_frame,
                                bg=self.colors['panel_bg'],
                                relief=tk.SOLID,
                                borderwidth=1,
                                padx=15,
                                pady=15)
        book_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(book_info_frame,
                text="📖 اطلاعات کتاب انتخاب‌شده",
                font=self.fonts['subheader'],
                bg=self.colors['panel_bg'],
                fg=self.colors['primary']).pack(anchor='center', pady=(0, 10))
        
        info_fields = [
            ("عنوان:", "selected_title"),
            ("نویسنده:", "selected_author"),
            ("موجودی:", "selected_quantity"),
            ("وضعیت:", "selected_status"),
            ("امانت‌های فعال:", "selected_active_loans")
        ]
        
        for label_text, attr_name in info_fields:
            row_frame = tk.Frame(book_info_frame, bg=self.colors['panel_bg'])
            row_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(row_frame,
                    text=label_text,
                    font=self.fonts['small'],
                    bg=self.colors['panel_bg'],
                    fg=self.colors['dark'],
                    anchor='e',
                    width=15).pack(side=tk.RIGHT, padx=(10, 5))
            
            label = tk.Label(row_frame,
                        text="---",
                        font=self.fonts['small'],
                        bg=self.colors['panel_bg'],
                        fg=self.colors['primary'],
                        anchor='w')
            label.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            setattr(self, attr_name, label)
        
        # تنظیم تاریخ‌ها
        date_frame = tk.Frame(content_frame,
                            bg=self.colors['panel_bg'],
                            relief=tk.SOLID,
                            borderwidth=1,
                            padx=15,
                            pady=15)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(date_frame,
                text="📅 تنظیم تاریخ امانت",
                font=self.fonts['subheader'],
                bg=self.colors['panel_bg'],
                fg=self.colors['primary']).pack(anchor='center', pady=(0, 10))
        
        # تاریخ امانت
        borrow_frame = tk.Frame(date_frame, bg=self.colors['panel_bg'])
        borrow_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(borrow_frame,
                text="تاریخ امانت:",
                font=self.fonts['small'],
                bg=self.colors['panel_bg'],
                fg=self.colors['dark'],
                anchor='e',
                width=15).pack(side=tk.RIGHT, padx=(10, 5))
        
        self.borrow_date_entry = tk.Entry(borrow_frame,
                                        font=self.fonts['small'],
                                        bg='white',
                                        fg='black',
                                        relief=tk.SOLID,
                                        borderwidth=1,
                                        justify='right')
        self.borrow_date_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=3)
        
        tk.Button(borrow_frame,
                text="امروز",
                command=self.set_borrow_today,
                font=self.fonts['small'],
                bg=self.colors['info'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=1,
                padx=10,
                pady=2,
                cursor='hand2').pack(side=tk.RIGHT, padx=(5, 0))
        
        # تاریخ بازگشت
        return_frame = tk.Frame(date_frame, bg=self.colors['panel_bg'])
        return_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(return_frame,
                text="تاریخ بازگشت:",
                font=self.fonts['small'],
                bg=self.colors['panel_bg'],
                fg=self.colors['dark'],
                anchor='e',
                width=15).pack(side=tk.RIGHT, padx=(10, 5))
        
        self.return_date_entry = tk.Entry(return_frame,
                                        font=self.fonts['small'],
                                        bg='white',
                                        fg='black',
                                        relief=tk.SOLID,
                                        borderwidth=1,
                                        justify='right')
        self.return_date_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=3)
        
        tk.Button(return_frame,
                text="+۱۴ روز",
                command=self.set_return_14_days,
                font=self.fonts['small'],
                bg=self.colors['info'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=1,
                padx=10,
                pady=2,
                cursor='hand2').pack(side=tk.RIGHT, padx=(5, 0))
        
        # دکمه اعمال تاریخ‌ها
        apply_frame = tk.Frame(date_frame, bg=self.colors['panel_bg'])
        apply_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(apply_frame,
                text="✅ اعمال تاریخ‌ها",
                command=self.apply_dates,
                font=self.fonts['small'],
                bg=self.colors['success'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=2,
                padx=20,
                pady=5,
                cursor='hand2').pack(side=tk.RIGHT)
        
        # دکمه باز کردن داشبورد کامل
        dashboard_btn_frame = tk.Frame(content_frame,
                                    bg=self.colors['panel_bg'])
        dashboard_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(dashboard_btn_frame,
                text="📊 باز کردن داشبورد یادآوری کامل",
                command=self.open_reminder_dashboard,
                font=self.fonts['small'],
                bg=self.colors['secondary'],
                fg='white',
                relief=tk.RAISED,
                borderwidth=2,
                padx=20,
                pady=8,
                cursor='hand2').pack(fill=tk.X)
        
        # آمار و گزارشات
        stats_frame = tk.Frame(content_frame,
                            bg=self.colors['panel_bg'],
                            relief=tk.SOLID,
                            borderwidth=1,
                            padx=15,
                            pady=15)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(stats_frame,
                text="📊 آمار کتابخانه",
                font=self.fonts['subheader'],
                bg=self.colors['panel_bg'],
                fg=self.colors['primary']).pack(anchor='center', pady=(0, 10))
        
        self.stats_label = tk.Label(stats_frame,
                                text="در حال بارگذاری...",
                                font=self.fonts['normal'],
                                bg=self.colors['panel_bg'],
                                fg=self.colors['dark'],
                                justify=tk.RIGHT,
                                wraplength=300)
        self.stats_label.pack(anchor='center', fill=tk.X)

    def setup_bottom_panel(self):
        """تنظیم پنل پایین - مدیریت سوابق"""
        content_frame = tk.Frame(self.bottom_panel,
                                bg=self.colors['panel_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # هشدار حذف
        warning_frame = tk.Frame(content_frame,
                                bg=self.colors['panel_bg'])
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(warning_frame,
                text="⚠️ مدیریت حذف سوابق امانت",
                font=self.fonts['subheader'],
                bg=self.colors['panel_bg'],
                fg=self.colors['danger']).pack(anchor='center', pady=(0, 10))
        
        warning_text = ("با حذف تاریخچه، تمام سوابق امانت‌های گذشته پاک می‌شوند. "
                    "این عمل غیرقابل بازگشت است.")
        tk.Label(warning_frame,
                text=warning_text,
                font=self.fonts['small'],
                bg=self.colors['panel_bg'],
                fg=self.colors['dark'],
                wraplength=600,
                justify=tk.CENTER).pack()
        
        # دکمه حذف کامل
        self.delete_history_btn = tk.Button(content_frame,
                                        text="🗑️ حذف کامل تاریخچه امانت‌ها",
                                        command=self.delete_all_history,
                                        font=('Tahoma', 11, 'bold'),
                                        bg=self.colors['danger'],
                                        fg='white',
                                        relief=tk.RAISED,
                                        borderwidth=2,
                                        padx=30,
                                        pady=10,
                                        cursor='hand2')
        self.delete_history_btn.pack(pady=(0, 20))
        
        # دکمه‌های حذف انتخابی
        selective_frame = tk.Frame(content_frame, bg=self.colors['panel_bg'])
        selective_frame.pack(fill=tk.X)
        
        selective_buttons = [
            ("حذف انتخابی", self.selective_history_deletion, self.colors['secondary']),
            ("حذف سوابق قدیمی", self.delete_old_history, self.colors['warning']),
            ("حذف کاربران غیرفعال", self.delete_inactive_users_history, self.colors['info'])
        ]
        
        for text, command, color in selective_buttons:
            btn = tk.Button(selective_frame,
                        text=text,
                        command=command,
                        font=self.fonts['small'],
                        bg=color,
                        fg='white',
                        relief=tk.RAISED,
                        borderwidth=1,
                        padx=15,
                        pady=5,
                        cursor='hand2')
            btn.pack(side=tk.RIGHT, padx=10)

    def bind_mouse_scroll_all(self):
        """اتصال اسکرول ماوس به ویجت‌ها"""
        def bind_scroll(widget):
            widget.bind("<Enter>", lambda e: self._bind_scroll_to_widget(widget))
            widget.bind("<Leave>", lambda e: self._unbind_scroll_from_widget())
        
        bind_scroll(self.canvas)
        if hasattr(self, 'tree'):
            bind_scroll(self.tree)
        if hasattr(self, 'users_tree'):
            bind_scroll(self.users_tree)

    def _bind_scroll_to_widget(self, widget):
        """اتصال اسکرول ماوس به ویجت مشخص"""
        if isinstance(widget, tk.Canvas):
            widget.bind_all("<MouseWheel>", self._on_mousewheel_vertical)
            widget.bind_all("<Shift-MouseWheel>", self._on_mousewheel_horizontal)
            widget.bind_all("<Button-4>", self._on_mousewheel_vertical)
            widget.bind_all("<Button-5>", self._on_mousewheel_vertical)
            widget.bind_all("<Shift-Button-4>", self._on_mousewheel_horizontal)
            widget.bind_all("<Shift-Button-5>", self._on_mousewheel_horizontal)
        elif isinstance(widget, ttk.Treeview):
            widget.bind("<MouseWheel>", lambda e: self._on_treeview_scroll(e, widget))
            widget.bind("<Button-4>", lambda e: self._on_treeview_scroll(e, widget))
            widget.bind("<Button-5>", lambda e: self._on_treeview_scroll(e, widget))

    def _unbind_scroll_from_widget(self):
        """لغو اتصال اسکرول ماوس"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        self.canvas.unbind_all("<Shift-Button-4>")
        self.canvas.unbind_all("<Shift-Button-5>")

    def _on_mousewheel_vertical(self, event):
        """مدیریت اسکرول عمودی"""
        if event.delta:
            scroll_amount = int(-1 * (event.delta / 120))
        elif event.num == 4:
            scroll_amount = -1
        elif event.num == 5:
            scroll_amount = 1
        else:
            return
        
        self.canvas.yview_scroll(scroll_amount, "units")

    def _on_mousewheel_horizontal(self, event):
        """مدیریت اسکرول افقی"""
        if event.delta:
            scroll_amount = int(-1 * (event.delta / 120))
        elif event.num == 4:
            scroll_amount = -1
        elif event.num == 5:
            scroll_amount = 1
        else:
            return
        
        self.canvas.xview_scroll(scroll_amount, "units")

    def _on_treeview_scroll(self, event, treeview):
        """مدیریت اسکرول Treeview"""
        if event.delta:
            scroll_amount = int(-1 * (event.delta / 120))
        elif event.num == 4:
            scroll_amount = -1
        elif event.num == 5:
            scroll_amount = 1
        else:
            return
        
        treeview.yview_scroll(scroll_amount, "units")

    # ===== متدهای اصلی =====
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_books = json.load(f)
                    self.books = []
                    for book in loaded_books:
                        if 'translator' not in book:
                            book['translator'] = ''
                        if 'year' not in book:
                            book['year'] = ''
                        if 'publisher' not in book:
                            book['publisher'] = ''
                        if 'quantity' not in book:
                            book['quantity'] = 1
                        if 'active_loans' not in book:
                            book['active_loans'] = []
                        if 'loan_history' not in book:
                            book['loan_history'] = []
                        self.books.append(book)
            except Exception as e:
                messagebox.showerror("خطا", f"بارگذاری اطلاعات کتاب‌ها ناموفق بود: {str(e)}")
                self.books = self.get_sample_books()
        else:
            self.books = self.get_sample_books()

        if os.path.exists(self.users_data_file):
            try:
                with open(self.users_data_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except Exception as e:
                messagebox.showerror("خطا", f"بارگزاری اطلاعات کاربران ناموفق بود: {str(e)}")
                self.users = []
        else:
            self.users = []

        self.save_data()

    def reload_data(self):
        try:
            self.books = []
            self.users = []
            self.load_data()
            self.migrate_old_data()
            if hasattr(self, 'dashboard_tree') and self.dashboard_tree.winfo_exists():
                self.dashboard_tree.delete(*self.dashboard_tree.get_children())
                self.update_dashboard_list()  # کال متد جدید
            messagebox.showinfo("ریفرش موفق", "داده‌ها به‌روزرسانی شدند.", parent=self.root)
        except Exception as e:
            messagebox.showerror("خطا", f"مشکل ریفرش: {str(e)}", parent=self.root)
            print(f"Error: {str(e)}")  # کنسول چک کن

    def update_dashboard_list(self):
        active_loans = []
        for book in self.books:
            for loan in book.get('active_loans', []):
                days_diff = self.calculate_days_difference(loan['return_date'])  # اگر فانکشن نداری، از telegram_bot کپی کن
                active_loans.append({
                    'borrower_name': loan['borrower_name'],
                    'borrower_id': loan['borrower_id'],
                    'book_title': book['book_name'],
                    'borrow_date': loan['borrow_date'],
                    'return_date': loan['return_date'],
                    'days_diff': days_diff
                })
        for loan in active_loans:
            status = "عادی" if loan['days_diff'] > 0 else "هشدار" if loan['days_diff'] == 0 else "معوق"
            self.dashboard_tree.insert('', tk.END, values=(
                loan['borrower_name'], loan['borrower_id'], loan['book_title'],
                loan['borrow_date'], loan['return_date'], status, loan['days_diff']
            ))

    def update_dashboard_list(self):
        """آپدیت لیست Treeview در داشبورد"""
        if not hasattr(self, 'dashboard_tree'):
            return
        
        # فرض بر لیست امانت‌ها (از کد شما اقتباس)
        active_loans = []  # لیست امانت‌های فعال رو دوباره بساز
        for book in self.books:
            for loan in book.get('active_loans', []):
                days_diff = self.calculate_days_difference(loan['return_date'])  # اگر فانکشن دارید
                active_loans.append({
                    'borrower_name': loan['borrower_name'],
                    'borrower_id': loan['borrower_id'],
                    'book_title': book['book_name'],
                    'borrow_date': loan['borrow_date'],
                    'return_date': loan['return_date'],
                    'days_diff': days_diff
                })
        
        # پر کردن Treeview
        for loan in active_loans:
            status = "عادی" if loan['days_diff'] > 0 else "هشدار" if loan['days_diff'] == 0 else "معوق"
            self.dashboard_tree.insert('', tk.END, values=(
                loan['borrower_name'],
                loan['borrower_id'],
                loan['book_title'],
                loan['borrow_date'],
                loan['return_date'],
                status,
                loan['days_diff']
            ))

    def get_sample_books(self):
        return [
            {
                'book_name': 'شازده کوچولو',
                'author': 'آنتوان دو سنت اگزوپری',
                'translator': 'احمد شاملو',
                'year': '1379',
                'publisher': 'نگاه',
                'quantity': 3,
                'active_loans': [],
                'loan_history': []
            },
            {
                'book_name': 'ملت عشق',
                'author': 'الیف شافاک',
                'translator': 'ارسلان فصیحی',
                'year': '1393',
                'publisher': 'ققنوس',
                'quantity': 2,
                'active_loans': [
                    {
                        'borrower_name': 'علی محمدی',
                        'borrower_id': '40123456789012',
                        'borrow_date': '1402-10-25',
                        'return_date': '1402-11-09',
                        'returned': False
                    }
                ],
                'loan_history': []
            }
        ]

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("خطا", f"ذخیره اطلاعات کتاب‌ها ناموفق بود: {str(e)}")

        try:
            with open(self.users_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("خطا", f"ذخیره اطلاعات کاربران ناموفق بود: {str(e)}")

    def migrate_old_data(self):
        for book in self.books:
            if 'active_loans' not in book:
                book['active_loans'] = []
                book['loan_history'] = []
                
                if book.get('status') == 'Borrowed' and book.get('borrower_name'):
                    loan = {
                        'borrower_name': book.get('borrower_name', ''),
                        'borrower_id': book.get('borrower_id', ''),
                        'borrow_date': book.get('borrow_date', ''),
                        'return_date': book.get('return_date', ''),
                        'returned': False
                    }
                    book['active_loans'].append(loan)
                    
                old_fields = ['borrower_name', 'borrower_id', 'borrow_date', 'return_date', 'status']
                for field in old_fields:
                    if field in book:
                        del book[field]
        
        self.save_data()

    def update_display(self, books=None):
        if books is None:
            books = self.books
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for book in books:
            current_quantity = book.get('quantity', 1)
            
            if current_quantity > 0:
                status_text = 'در دسترس'
            else:
                status_text = 'امانت داده شده'
            
            self.tree.insert('', tk.END, values=(
                book.get('book_name', ''),
                book.get('author', ''),
                book.get('publish_year', ''),
                current_quantity,
                status_text
            ))

    def search_books(self, event=None):
        query = self.search_entry.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for book in self.books:
            if (query in book['book_name'].lower() or 
                query in book['author'].lower() or
                query in book.get('translator', '').lower() or
                query in book.get('publisher', '').lower()):
                
                current_quantity = book.get('quantity', 1)
                
                if current_quantity > 0:
                    status_text = 'در دسترس'
                else:
                    status_text = 'امانت داده شده'
                
                self.tree.insert("", "end", values=(
                    book['book_name'], book['author'], 
                    book.get('publish_year', ''), current_quantity, status_text
                ))

    def on_book_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            book_index = self.tree.index(item)
            if book_index < len(self.books):
                book = self.books[book_index]
                self.update_selected_book_info(book)

    def on_user_select(self, event):
        """هنگام انتخاب کاربر از لیست"""
        selection = self.users_tree.selection()
        if selection:
            item = selection[0]
            user_index = self.users_tree.index(item)
            if user_index < len(self.users):
                user = self.users[user_index]
                self.current_user = user
                self.current_user_label.config(text=f"{user['first_name']} {user['last_name']}")

    def update_selected_book_info(self, book):
        self.selected_title.config(text=book['book_name'])
        self.selected_author.config(text=book['author'])
        self.selected_quantity.config(text=f"{book.get('quantity', 1)} نسخه")
        
        current_quantity = book.get('quantity', 1)
        if current_quantity > 0:
            status_text = 'در دسترس'
        else:
            status_text = 'امانت داده شده'
        
        self.selected_status.config(text=status_text)
        
        active_loans = book.get('active_loans', [])
        active_loans_count = len(active_loans)
        self.selected_active_loans.config(text=str(active_loans_count))

    def set_borrow_today(self):
        today = jdatetime.date.today().strftime("%Y-%m-%d")
        self.borrow_date_entry.delete(0, tk.END)
        self.borrow_date_entry.insert(0, today)

    def set_return_14_days(self):
        return_date = (jdatetime.date.today() + jdatetime.timedelta(days=14)).strftime("%Y-%m-%d")
        self.return_date_entry.delete(0, tk.END)
        self.return_date_entry.insert(0, return_date)

    def apply_dates(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً ابتدا یک کتاب انتخاب کنید")
            return
        if not self.current_user:
            messagebox.showwarning("خطا", "لطفاً ابتدا اطلاعات کاربر را ذخیره کنید")
            return

        borrow_date = self.borrow_date_entry.get().strip()
        return_date = self.return_date_entry.get().strip()
        if not borrow_date or not return_date:
            messagebox.showwarning("خطا", "لطفاً هر دو تاریخ امانت و بازگشت را وارد کنید")
            return

        try:
            jdatetime.datetime.strptime(borrow_date, "%Y-%m-%d")
            jdatetime.datetime.strptime(return_date, "%Y-%m-%d")
        except Exception:
            messagebox.showwarning("فرمت تاریخ نامعتبر", "لطفاً تاریخ‌ها را با فرمت YYYY-MM-DD (شمسی) وارد کنید.")
            return

        item = selection[0]
        book_index = self.tree.index(item)
        if book_index < len(self.books):
            book = self.books[book_index]
            
            if book.get('quantity', 0) <= 0:
                messagebox.showwarning("خطا", "موجودی این کتاب صفر است، نمی‌توان امانت داد")
                return
            
            new_loan = {
                'borrower_name': f"{self.current_user['first_name']} {self.current_user['last_name']}",
                'borrower_id': self.current_user['student_id'],
                'borrow_date': borrow_date,
                'return_date': return_date,
                'returned': False
            }
            
            if 'active_loans' not in book:
                book['active_loans'] = []
            book['active_loans'].append(new_loan)
            
            book['quantity'] = book.get('quantity', 1) - 1
            
            for user in self.users:
                if user.get('student_id') == self.current_user['student_id']:
                    if 'history' not in user:
                        user['history'] = []
                    transaction = {
                        'book_title': book['book_name'],
                        'author': book['author'],
                        'borrow_date': borrow_date,
                        'return_date': return_date,
                        'status': 'Borrowed'
                    }
                    user['history'].append(transaction)
                    break
            
            self.save_data()
            self.update_display()
            self.update_stats()
            self.update_selected_book_info(book)
            messagebox.showinfo("موفقیت", "تاریخ‌ها با موفقیت ثبت شدند")

    def save_user_info(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        student_id = self.student_id_entry.get().strip()
        email = self.email_entry.get().strip()

        if not first_name or not last_name or not student_id or not phone:
            messagebox.showwarning("خطا", "لطفاً تمام فیلدهای ضروری را پر کنید. (ایمیل اختیاری است)")
            return

        if not student_id.isdigit() or len(student_id) != 14:
            messagebox.showwarning("خطا", "شماره دانشجویی باید دقیقاً ۱۴ رقم باشد.")
            return

        for user in self.users:
            if user.get('student_id') == student_id:
                if not self.current_user or self.current_user.get('student_id') != student_id:
                    messagebox.showwarning("خطا", "این شماره دانشجویی قبلاً ثبت شده است!")
                    return
    
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('09'):
            messagebox.showwarning("خطا", "شماره تماس باید ۱۱ رقم و با 09 شروع شود.")
            return

        if email and ('@' not in email or '.' not in email):
            messagebox.showwarning("خطا", "لطفاً یک ایمیل معتبر وارد کنید.")
            return

        self.current_user = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'student_id': student_id,
            'email': email,
            'telegram_chat_id': None
        }

        self.current_user_label.config(text=f"{first_name} {last_name}")

        user_exists = False
        for user in self.users:
            if user.get('student_id') == student_id:
                user.update(self.current_user)
                user_exists = True
                break
                
        if not user_exists:
            u = self.current_user.copy()
            if 'history' not in u:
                u['history'] = []
            self.users.append(u)

        self.save_data()
        self.update_users_display()
        
        messagebox.showinfo(
            "موفقیت", 
            f"✅ اطلاعات کاربر با موفقیت ذخیره شد\n\n"
            f"👤 نام: {first_name} {last_name}\n"
            f"🎫 شماره دانشجویی: {student_id}\n"
            f"📞 تلفن: {phone}"
        )

    def clear_user_info(self):
        for entry in [self.first_name_entry, self.last_name_entry, 
                    self.phone_entry, self.student_id_entry, self.email_entry]:
            entry.delete(0, tk.END)
        
        self.current_user = None
        self.current_user_label.config(text="هیچ کاربری انتخاب نشده")

    def clear_selection(self):
        self.tree.selection_remove(self.tree.selection())
        self.selected_title.config(text="---")
        self.selected_author.config(text="---")
        self.selected_quantity.config(text="---")
        self.selected_status.config(text="---")
        self.selected_active_loans.config(text="---")
        self.clear_date_fields()

    def clear_date_fields(self):
        self.borrow_date_entry.delete(0, tk.END)
        self.return_date_entry.delete(0, tk.END)

    def update_stats(self):
        total_books = len(self.books)
        total_copies = sum(book.get('quantity', 1) for book in self.books)
        active_loans_count = sum(len(book.get('active_loans', [])) for book in self.books)
        total_users = len(self.users)
        
        stats_text = (f"📚 تعداد کتاب‌ها: {total_books}\n"
                    f"🔢 تعداد نسخه‌ها: {total_copies}\n"
                    f"📥 امانت‌های فعال: {active_loans_count}\n"
                    f"👥 کاربران ثبت‌شده: {total_users}")
        
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text=stats_text)

    def update_users_display(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        for user in self.users:
            self.users_tree.insert('', tk.END, values=(
                user.get('first_name', ''),
                user.get('last_name', ''),
                user.get('student_id', ''),
                user.get('phone', ''),
                user.get('email', '')
            ))

    def delete_selected_user(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً یک کاربر را برای حذف انتخاب کنید.")
            return
        
        item = selection[0]
        user_index = self.users_tree.index(item)
        if user_index < len(self.users):
            user = self.users[user_index]
            
            borrowed_books = []
            for book in self.books:
                for loan in book.get('active_loans', []):
                    if loan.get('borrower_id') == user.get('student_id'):
                        borrowed_books.append(f"{book['book_name']} (تاریخ بازگشت: {loan.get('return_date', '')})")
            
            if borrowed_books:
                books_list = "\n".join(f"• {book}" for book in borrowed_books)
                messagebox.showwarning(
                    "خطا", 
                    f"کاربر '{user['first_name']} {user['last_name']}' در حال حاضر کتاب‌های زیر را امانت گرفته است:\n\n"
                    f"{books_list}\n\n"
                    "لطفاً ابتدا کتاب‌ها بازگردانده شوند سپس اقدام به حذف کاربر کنید."
                )
                return
            
            result = messagebox.askyesno(
                "تأیید حذف کاربر",
                f"آیا از حذف کاربر زیر مطمئن هستید؟\n\n"
                f"👤 نام: {user['first_name']} {user['last_name']}\n"
                f"🎫 شماره دانشجویی: {user['student_id']}\n"
                f"📞 تلفن: {user['phone']}\n\n"
                f"⚠️ این عمل غیرقابل بازگشت است!"
            )
            
            if result:
                try:
                    if self.current_user and self.current_user.get('student_id') == user.get('student_id'):
                        self.current_user = None
                        self.current_user_label.config(text="هیچ کاربری انتخاب نشده")
                    
                    del self.users[user_index]
                    self.save_data()
                    self.update_users_display()
                    messagebox.showinfo("موفقیت", "کاربر با موفقیت از سیستم حذف شد.")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در حذف کاربر: {str(e)}")

    def select_user_from_list(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً یک کاربر از لیست انتخاب کنید.")
            return
        
        item = selection[0]
        user_index = self.users_tree.index(item)
        if user_index < len(self.users):
            user = self.users[user_index]
            
            self.current_user = user
            self.current_user_label.config(text=f"{user['first_name']} {user['last_name']}")
            
            messagebox.showinfo(
                "انتخاب کاربر", 
                f"کاربر '{user['first_name']} {user['last_name']}' با موفقیت انتخاب شد.\n"
                f"شماره دانشجویی: {user['student_id']}"
            )

    def delete_selected_book(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً یک کتاب را برای حذف انتخاب کنید.")
            return
        
        item = selection[0]
        book_index = self.tree.index(item)
        if book_index < len(self.books):
            book = self.books[book_index]
            
            active_loans = book.get('active_loans', [])
            if active_loans:
                messagebox.showwarning(
                    "خطا", 
                    f"کتاب '{book['book_name']}' در حال حاضر {len(active_loans)} امانت فعال دارد.\n"
                    "لطفاً ابتدا تمام امانت‌ها برگردانده شود سپس اقدام به حذف کنید."
                )
                return
            
            result = messagebox.askyesno(
                "تأیید حذف کتاب",
                f"آیا از حذف کتاب زیر مطمئن هستید؟\n\n"
                f"📖 عنوان: {book['book_name']}\n"
                f"✍️ نویسنده: {book['author']}\n"
                f"🔢 تعداد موجودی: {book.get('quantity', 1)}\n\n"
                f"⚠️ این عمل غیرقابل بازگشت است!"
            )
            
            if result:
                try:
                    del self.books[book_index]
                    self.save_data()
                    self.update_display()
                    self.update_stats()
                    self.clear_selection()
                    messagebox.showinfo("موفقیت", "کتاب با موفقیت از کتابخانه حذف شد.")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در حذف کتاب: {str(e)}")

    def refresh_data(self):
        self.load_data()
        self.update_display()
        self.update_stats()
        self.update_users_display()
        self.clear_selection()
        if self.current_user:
            self.current_user_label.config(text=f"{self.current_user['first_name']} {self.current_user['last_name']}")
        messagebox.showinfo("بروزرسانی", "✅ تمام داده‌ها با موفقیت بروزرسانی شدند.")

    def open_reminder_dashboard(self):
        """باز کردن داشبورد یادآوری کامل در پنجره جدید"""
        self.dashboard_dialog = tk.Toplevel(self.root)
        dashboard_window = tk.Toplevel(self.root)
        dashboard_window.title("📊 داشبورد کامل یادآوری امانت‌ها")
        dashboard_window.geometry("1000x700")
        dashboard_window.configure(bg=self.colors['bg_light'])
        
        # هدر
        header_frame = tk.Frame(dashboard_window, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame,
                text="📊 داشبورد کامل یادآوری امانت‌ها",
                font=('Tahoma', 18, 'bold'),
                bg=self.colors['primary'],
                fg='white').pack(expand=True, fill=tk.BOTH)
        
        tk.Label(header_frame,
                text="روی هر دسته کلیک کنید تا جزئیات آن را مشاهده کنید",
                font=('Tahoma', 11),
                bg=self.colors['primary'],
                fg='#e9ecef').pack()
        
        # کانتینر اصلی
        main_container = tk.Frame(dashboard_window, bg=self.colors['bg_light'], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # سه حالت اصلی
        status_container = tk.Frame(main_container, bg=self.colors['bg_light'])
        status_container.pack(fill=tk.X, pady=(0, 20))
        
        # حالت عادی
        self.dash_normal_frame = tk.Frame(status_container,
                                        bg='#d4edda',
                                        relief=tk.RAISED,
                                        borderwidth=3,
                                        padx=30,
                                        pady=25,
                                        cursor='hand2')
        self.dash_normal_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        self.dash_normal_frame.bind('<Button-1>', lambda e: self.show_normal_details_dashboard())
        
        tk.Label(self.dash_normal_frame,
                text="✅ عادی",
                font=('Tahoma', 16, 'bold'),
                bg='#d4edda',
                fg='#155724',
                cursor='hand2').pack(pady=(0, 10))
        
        self.dash_normal_count = tk.Label(self.dash_normal_frame,
                                        text="0 مورد",
                                        font=('Tahoma', 24, 'bold'),
                                        bg='#d4edda',
                                        fg='#155724',
                                        cursor='hand2')
        self.dash_normal_count.pack()
        
        tk.Label(self.dash_normal_frame,
                text="بیش از ۳ روز مانده",
                font=('Tahoma', 11),
                bg='#d4edda',
                fg='#155724',
                cursor='hand2').pack(pady=(10, 0))
        
        # حالت نزدیک موعد
        self.dash_warning_frame = tk.Frame(status_container,
                                        bg='#fff3cd',
                                        relief=tk.RAISED,
                                        borderwidth=3,
                                        padx=30,
                                        pady=25,
                                        cursor='hand2')
        self.dash_warning_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        self.dash_warning_frame.bind('<Button-1>', lambda e: self.show_warning_details_dashboard())
        
        tk.Label(self.dash_warning_frame,
                text="⚠️ نزدیک موعد",
                font=('Tahoma', 16, 'bold'),
                bg='#fff3cd',
                fg='#856404',
                cursor='hand2').pack(pady=(0, 10))
        
        self.dash_warning_count = tk.Label(self.dash_warning_frame,
                                        text="0 مورد",
                                        font=('Tahoma', 24, 'bold'),
                                        bg='#fff3cd',
                                        fg='#856404',
                                        cursor='hand2')
        self.dash_warning_count.pack()
        
        tk.Label(self.dash_warning_frame,
                text="۱-۳ روز مانده",
                font=('Tahoma', 11),
                bg='#fff3cd',
                fg='#856404',
                cursor='hand2').pack(pady=(10, 0))
        
        # حالت معوق
        self.dash_overdue_frame = tk.Frame(status_container,
                                        bg='#f8d7da',
                                        relief=tk.RAISED,
                                        borderwidth=3,
                                        padx=30,
                                        pady=25,
                                        cursor='hand2')
        self.dash_overdue_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        self.dash_overdue_frame.bind('<Button-1>', lambda e: self.show_overdue_details_dashboard())
        
        tk.Label(self.dash_overdue_frame,
                text="⛔ معوق",
                font=('Tahoma', 16, 'bold'),
                bg='#f8d7da',
                fg='#721c24',
                cursor='hand2').pack(pady=(0, 10))
        
        self.dash_overdue_count = tk.Label(self.dash_overdue_frame,
                                        text="0 مورد",
                                        font=('Tahoma', 24, 'bold'),
                                        bg='#f8d7da',
                                        fg='#721c24',
                                        cursor='hand2')
        self.dash_overdue_count.pack()
        
        tk.Label(self.dash_overdue_frame,
                text="تاریخ گذشته",
                font=('Tahoma', 11),
                bg='#f8d7da',
                fg='#721c24',
                cursor='hand2').pack(pady=(10, 0))
        
        # Treeview برای نمایش جزئیات
        details_frame = tk.Frame(main_container, bg=self.colors['bg_light'])
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد Treeview با اسکرول افقی
        self.dashboard_tree = ttk.Treeview(details_frame,
                                        style="Custom.Treeview",
                                        columns=('نام کاربر', 'شماره دانشجویی', 'عنوان کتاب', 'تاریخ امانت', 'تاریخ بازگشت', 'روزهای مانده'),
                                        show='headings',
                                        height=15)
        
        columns = [
            ('نام کاربر', 180),
            ('شماره دانشجویی', 150),
            ('عنوان کتاب', 250),
            ('تاریخ امانت', 120),
            ('تاریخ بازگشت', 120),
            ('روزهای مانده', 120)
        ]
        
        for col, width in columns:
            self.dashboard_tree.heading(col, text=col, anchor='center')
            self.dashboard_tree.column(col, width=width, minwidth=width, anchor='center', stretch=False)
        
        # اسکرول‌بارهای عمودی و افقی
        tree_scrollbar_y = ttk.Scrollbar(details_frame,
                                        orient=tk.VERTICAL,
                                        command=self.dashboard_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(details_frame,
                                        orient=tk.HORIZONTAL,
                                        command=self.dashboard_tree.xview)
        
        self.dashboard_tree.configure(yscrollcommand=tree_scrollbar_y.set,
                                    xscrollcommand=tree_scrollbar_x.set)
        
        self.dashboard_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # فریم جدید برای دکمه‌ها در داشبورد (اضافه‌شده برای ارسال پیام)
        button_frame = tk.Frame(details_frame, bg=self.colors['bg_light'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_frame = tk.Frame(details_frame, bg=self.colors['bg_light'])
        refresh_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(refresh_frame,  # اگر از کلاس ModernButton استفاده می‌کنی
            text="🔄 ریفرش داده‌ها",
            command=self.reload_data,
            bg=self.colors['info'],
            fg='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=8,
            cursor='hand2').pack(fill=tk.X, padx=10)

        # دکمه ارسال پیام تلگرام به انتخابی
        tk.Button(button_frame,
                text="📱 ارسال پیام تلگرام به انتخابی",
                command=self.send_telegram_for_selected_loan,
                font=self.fonts['small'],
                bg='#0088cc',
                fg='white',
                relief=tk.RAISED,
                borderwidth=2,
                padx=20,
                pady=8,
                cursor='hand2').pack(side=tk.LEFT, padx=10)

        # برچسب اطلاعات
        self.dashboard_info_label = tk.Label(main_container,
                                            text="برای مشاهده جزئیات، روی یکی از دسته‌های بالا کلیک کنید.",
                                            font=self.fonts['normal'],
                                            bg=self.colors['bg_light'],
                                            fg=self.colors['dark'])
        self.dashboard_info_label.pack(fill=tk.X, pady=(10, 0))
        
        # بروزرسانی اولیه
        self.update_dashboard_counts()
        self.current_category = None

    def update_dashboard_counts(self):
        """بروزرسانی تعداد در داشبورد کامل"""
        try:
            today = jdatetime.date.today()
            normal_count = 0
            warning_count = 0
            overdue_count = 0
            
            self.dashboard_normal_loans = []
            self.dashboard_warning_loans = []
            self.dashboard_overdue_loans = []
        
            for book in self.books:
                for loan in book.get('active_loans', []):
                    if loan.get('return_date'):
                        try:
                            return_date = jdatetime.datetime.strptime(loan['return_date'], "%Y-%m-%d").date()
                            days_remaining = (return_date - today).days
                            
                            loan_data = {
                                'borrower_name': loan.get('borrower_name', ''),
                                'borrower_id': loan.get('borrower_id', ''),
                                'book_title': book['book_name'],
                                'borrow_date': loan.get('borrow_date', ''),
                                'return_date': loan['return_date'],
                                'days_remaining': days_remaining
                            }
                        
                            if days_remaining < 0:
                                overdue_count += 1
                                self.dashboard_overdue_loans.append(loan_data)
                            elif days_remaining <= 3:
                                warning_count += 1
                                self.dashboard_warning_loans.append(loan_data)
                            else:
                                normal_count += 1
                                self.dashboard_normal_loans.append(loan_data)
                        except:
                            continue
        
            # به‌روزرسانی برچسب‌ها
            self.dash_normal_count.config(text=f"{normal_count} مورد")
            self.dash_warning_count.config(text=f"{warning_count} مورد")
            self.dash_overdue_count.config(text=f"{overdue_count} مورد")
            
        except Exception as e:
            print(f"خطا در بروزرسانی داشبورد کامل: {str(e)}")

    def show_normal_details_dashboard(self):
        """نمایش جزئیات امانت‌های عادی در داشبورد"""
        self.current_category = 'normal'
        self.update_dashboard_tree(self.dashboard_normal_loans, "✅ امانت‌های عادی (بیش از ۳ روز مانده)")

    def show_warning_details_dashboard(self):
        """نمایش جزئیات امانت‌های نزدیک موعد در داشبورد"""
        self.current_category = 'warning'
        self.update_dashboard_tree(self.dashboard_warning_loans, "⚠️ امانت‌های نزدیک موعد (۱-۳ روز مانده)")

    def show_overdue_details_dashboard(self):
        """نمایش جزئیات امانت‌های معوق در داشبورد"""
        self.current_category = 'overdue'
        self.update_dashboard_tree(self.dashboard_overdue_loans, "⛔ امانت‌های معوق (تاریخ گذشته)")

    def update_dashboard_tree(self, loans, title):
        """بروزرسانی Treeview در داشبورد"""
        # پاک کردن موارد قبلی
        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)
        
        # به‌روزرسانی برچسب اطلاعات
        self.dashboard_info_label.config(
            text=f"{title} - {len(loans)} مورد یافت شد.",
            fg=self.colors['success'] if len(loans) > 0 else self.colors['danger']
        )
        
        # اضافه کردن موارد جدید
        for loan in loans:
            days_text = f"{loan['days_remaining']} روز"
            if loan['days_remaining'] < 0:
                days_text = f"{-loan['days_remaining']} روز گذشته"
            
            self.dashboard_tree.insert('', tk.END, values=(
                loan['borrower_name'],
                loan['borrower_id'],
                loan['book_title'],
                loan['borrow_date'],
                loan['return_date'],
                days_text
            ))

    def send_telegram_to_all(self):
        """ارسال پیام تلگرام به همه کاربرانی که کتاب امانت دارند"""
        if not self.telegram_config.get('bot_token'):
            messagebox.showwarning("خطا", "لطفاً ابتدا توکن ربات تلگرام را تنظیم کنید.")
            return
        
        # جمع‌آوری همه وام‌های فعال
        all_loans = []
        for book in self.books:
            for loan in book.get('active_loans', []):
                all_loans.append({
                    'borrower_name': loan.get('borrower_name', ''),
                    'borrower_id': loan.get('borrower_id', ''),
                    'book_title': book['book_name'],
                    'borrow_date': loan.get('borrow_date', ''),
                    'return_date': loan.get('return_date', '')
                })
        
        if not all_loans:
            messagebox.showinfo("اطلاعات", "هیچ امانت فعالی یافت نشد.")
            return
        
        result = messagebox.askyesno(
            "تأیید ارسال پیام",
            f"آیا می‌خواهید پیام تلگرام برای {len(all_loans)} کاربر ارسال شود؟"
        )
        
        if not result:
            return
        
        success_count = 0
        failed_count = 0
        
        for loan in all_loans:
            # یافتن شماره تلفن کاربر
            user_phone = None
            for user in self.users:
                if user.get('student_id') == loan['borrower_id']:
                    user_phone = user.get('phone')
                    break
            
            if user_phone:
                message = f"""
📚 یادآوری بازگشت کتاب از کتابخانه دانشگاه

👤 کاربر گرامی: {loan['borrower_name']}
📖 کتاب: {loan['book_title']}
📅 تاریخ امانت: {loan['borrow_date']}
⏰ تاریخ بازگشت: {loan['return_date']}

لطفاً کتاب را در موعد مقرر بازگردانید.

با تشکر
کتابخانه دانشگاه
"""
                
                if self.send_telegram_message_to_user(user_phone, message):
                    success_count += 1
                else:
                    failed_count += 1
        
        messagebox.showinfo(
            "نتایج ارسال",
            f"📊 نتایج ارسال پیام تلگرام:\n\n"
            f"✅ ارسال موفق: {success_count} کاربر\n"
            f"❌ ارسال ناموفق: {failed_count} کاربر\n"
            f"📋 کل کاربران: {len(all_loans)}"
        )

    def send_telegram_message_to_user(self, phone, message):
        """ارسال پیام تلگرام به کاربر خاص"""
        try:
            bot_token = self.telegram_config.get('bot_token', '')
            chat_id = self.telegram_config.get('chat_id', '')
            
            if not bot_token or not chat_id:
                return False
            
            # ساخت پیام کامل
            full_message = f"{message}\n\n📞 تماس: {phone}"
            
            print(f"ارسال پیام تلگرام به {phone}:")
            print(full_message)
            
            return True
            
        except Exception as e:
            print(f"خطا در ارسال پیام تلگرام: {str(e)}")
            return False

    def check_overdue_books(self):
        try:
            today = jdatetime.date.today()
            overdue_count = 0
            
            for book in self.books:
                for loan in book.get('active_loans', []):
                    if loan.get('return_date'):
                        try:
                            return_date = jdatetime.datetime.strptime(loan['return_date'], "%Y-%m-%d").date()
                            days_remaining = (return_date - today).days
                            
                            if days_remaining < 0:
                                overdue_count += 1
                        except:
                            continue
            
        except Exception as e:
            pass

    def borrow_book_dialog(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً یک کتاب را برای امانت انتخاب کنید")
            return
            
        if not self.current_user:
            messagebox.showwarning("خطا", "لطفاً ابتدا یک کاربر را انتخاب یا ثبت کنید")
            return

        item = selection[0]
        book_index = self.tree.index(item)
        if book_index < len(self.books):
            book = self.books[book_index]
            
            current_quantity = book.get('quantity', 1)
            if current_quantity <= 0:
                messagebox.showwarning("ناموفق", "متأسفانه این کتاب در حال حاضر موجود نیست.")
                return

            result = messagebox.askyesno(
                "تأیید امانت",
                f"آیا از امانت دادن کتاب زیر مطمئن هستید؟\n\n"
                f"📖 کتاب: {book['book_name']}\n"
                f"✍️ نویسنده: {book['author']}\n"
                f"👤 کاربر: {self.current_user['first_name']} {self.current_user['last_name']}"
            )
            
            if not result:
                return

            book['quantity'] = current_quantity - 1
            
            borrow_date = jdatetime.date.today().strftime("%Y-%m-%d")
            return_date = (jdatetime.date.today() + jdatetime.timedelta(days=14)).strftime("%Y-%m-%d")
            
            new_loan = {
                'borrower_name': f"{self.current_user['first_name']} {self.current_user['last_name']}",
                'borrower_id': self.current_user['student_id'],
                'borrow_date': borrow_date,
                'return_date': return_date,
                'returned': False
            }
            
            if 'active_loans' not in book:
                book['active_loans'] = []
            book['active_loans'].append(new_loan)
            
            for user in self.users:
                if user.get('student_id') == self.current_user['student_id']:
                    if 'history' not in user:
                        user['history'] = []
                    transaction = {
                        'book_title': book['book_name'],
                        'author': book['author'],
                        'borrow_date': borrow_date,
                        'return_date': return_date,
                        'status': 'Borrowed'
                    }
                    user['history'].append(transaction)
                    break
            
            self.save_data()
            self.update_display()
            self.update_stats()
            self.update_selected_book_info(book)

            messagebox.showinfo(
                "موفقیت",
                f"✅ کتاب با موفقیت امانت داده شد\n\n"
                f"📖 کتاب: {book['book_name']}\n"
                f"👤 گیرنده: {new_loan['borrower_name']}\n"
                f"📅 تاریخ امانت: {borrow_date}\n"
                f"⏰ تاریخ بازگشت: {return_date}"
            )

    def return_book(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً یک کتاب را انتخاب کنید.")
            return
            
        item = selection[0]
        book_index = self.tree.index(item)
        if book_index < len(self.books):
            book = self.books[book_index]
            
            active_loans = book.get('active_loans', [])
            if not active_loans:
                messagebox.showwarning("خطا", "این کتاب امانت فعال ندارد")
                return
            
            # بازگرداندن همه امانت‌های فعال
            today = jdatetime.date.today().strftime("%Y-%m-%d")
            
            for loan in active_loans[:]:  # کپی از لیست برای حذف ایمن
                book['quantity'] = book.get('quantity', 0) + 1
                
                if 'loan_history' not in book:
                    book['loan_history'] = []
                
                loan_to_move = loan.copy()
                loan_to_move['returned'] = True
                loan_to_move['actual_return_date'] = today
                book['loan_history'].append(loan_to_move)
                
                # حذف از لیست active_loans
                book['active_loans'].remove(loan)
            
            self.save_data()
            self.update_display()
            self.update_stats()
            self.update_selected_book_info(book)
            
            messagebox.showinfo(
                "موفقیت", 
                f"✅ کتاب با موفقیت بازگردانده شد\n\n"
                f"📖 کتاب: {book['book_name']}\n"
                f"🔢 {len(active_loans)} امانت بازگردانده شد"
            )

    # ===== متدهای حذف تاریخچه =====

    def delete_all_history(self):
        has_history = False
        for book in self.books:
            if book.get('loan_history'):
                has_history = True
                break
        
        if not has_history:
            messagebox.showinfo("اطلاعات", "✅ هیچ تاریخچه‌ای برای حذف وجود ندارد.")
            return
        
        result = messagebox.askyesno(
            "⚠️ هشدار حذف کامل",
            "آیا مطمئن هستید که می‌خواهید تمام تاریخچه امانت‌ها را حذف کنید؟\n\n"
            "🔴 این عمل غیرقابل بازگشت است!\n"
            "🔴 تمام سوابق گذشته پاک می‌شوند!\n"
            "🔴 از پشتیبان‌گیری اطمینان حاصل کنید!\n\n"
            "برای تأیید، دوباره کلیک کنید:",
            icon='warning',
            default='no'
        )
        
        if not result:
            return
        
        original_text = self.delete_history_btn.cget('text')
        self.delete_history_btn.config(text="⏳ در حال حذف...", state='disabled')
        self.root.update()
        
        try:
            deleted_count = 0
            for book in self.books:
                if 'loan_history' in book:
                    deleted_count += len(book['loan_history'])
                    book['loan_history'] = []
            
            for user in self.users:
                if 'history' in user:
                    user['history'] = []
            
            self.save_data()
            
            self.delete_history_btn.config(
                text="✅ حذف کامل انجام شد",
                bg=self.colors['success'],
                state='normal'
            )
            
            messagebox.showinfo(
                "موفقیت",
                f"✅ تاریخچه امانت‌ها با موفقیت حذف شد.\n\n"
                f"📊 آمار حذف:\n"
                f"• {deleted_count} رکورد تاریخچه حذف شد\n"
                f"• {len(self.books)} کتاب بروزرسانی شد\n"
                f"• {len(self.users)} کاربر بروزرسانی شد"
            )
            
            self.root.after(2000, lambda: self.delete_history_btn.config(
                text=original_text,
                bg=self.colors['danger']
            ))
            
        except Exception as e:
            self.delete_history_btn.config(text=original_text, state='normal')
            messagebox.showerror("خطا", f"خطا در حذف تاریخچه: {str(e)}")

    def delete_old_history(self):
        today = jdatetime.date.today()
        one_year_ago = today - jdatetime.timedelta(days=365)
        
        deleted_count = 0
        for book in self.books:
            if 'loan_history' in book:
                old_count = len(book['loan_history'])
                book['loan_history'] = [
                    loan for loan in book['loan_history']
                    if jdatetime.datetime.strptime(loan.get('actual_return_date', '1400-01-01'), "%Y-%m-%d").date() > one_year_ago
                ]
                deleted_count += (old_count - len(book['loan_history']))
        
        if deleted_count > 0:
            self.save_data()
            messagebox.showinfo(
                "موفقیت",
                f"✅ تاریخچه قدیمی‌تر از یک سال حذف شد.\n\n"
                f"🗑️ {deleted_count} رکورد حذف شد."
            )
        else:
            messagebox.showinfo("اطلاعات", "✅ هیچ تاریخچه قدیمی‌ای یافت نشد.")

    def delete_inactive_users_history(self):
        active_users = set()
        for book in self.books:
            for loan in book.get('active_loans', []):
                active_users.add(loan.get('borrower_id'))
        
        deleted_count = 0
        for user in self.users:
            if user.get('student_id') not in active_users and 'history' in user:
                deleted_count += len(user['history'])
                user['history'] = []
        
        if deleted_count > 0:
            self.save_data()
            messagebox.showinfo(
                "موفقیت",
                f"✅ سوابق کاربران غیرفعال حذف شد.\n\n"
                f"👤 {len(self.users)} کاربر بررسی شد\n"
                f"🗑️ {deleted_count} رکورد حذف شد"
            )
        else:
            messagebox.showinfo("اطلاعات", "✅ هیچ سابقه‌ای برای کاربران غیرفعال یافت نشد.")

    def selective_history_deletion(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("🗂️ حذف انتخابی تاریخچه")
        dialog.geometry("600x500")
        dialog.configure(bg=self.colors['bg_light'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog,
                text="انتخاب تاریخچه برای حذف",
                font=self.fonts['subheader'],
                bg=self.colors['bg_light'],
                fg=self.colors['primary']).pack(pady=10)
        
        tree_frame = tk.Frame(dialog, bg=self.colors['bg_light'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('کتاب', 'تعداد تاریخچه'), show='headings', height=15)
        tree.heading('کتاب', text='عنوان کتاب')
        tree.heading('تعداد تاریخچه', text='تعداد رکوردها')
        tree.column('کتاب', width=300)
        tree.column('تعداد تاریخچه', width=150)
        
        book_indices = []
        for i, book in enumerate(self.books):
            if 'loan_history' in book and book['loan_history']:
                count = len(book['loan_history'])
                tree.insert('', tk.END, values=(book['book_name'], f"{count} رکورد"), tags=(str(i),))
                book_indices.append(i)
        
        if not book_indices:
            tk.Label(dialog,
                    text="✅ هیچ تاریخچه‌ای برای نمایش وجود ندارد.",
                    font=self.fonts['normal'],
                    bg=self.colors['bg_light']).pack(pady=50)
            
            tk.Button(dialog,
                    text="بستن",
                    command=dialog.destroy,
                    font=self.fonts['button'],
                    bg=self.colors['primary'],
                    fg='white',
                    padx=20,
                    pady=5).pack(pady=20)
            return
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=tree_scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def delete_selected():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("خطا", "لطفاً یک مورد را انتخاب کنید.")
                return
            
            for item in selection:
                book_idx = int(tree.item(item, "tags")[0])
                self.books[book_idx]['loan_history'] = []
            
            self.save_data()
            messagebox.showinfo("موفقیت", "تاریخچه‌های انتخاب شده حذف شدند.")
            dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg=self.colors['bg_light'])
        button_frame.pack(pady=10)
        
        tk.Button(button_frame,
                text="🗑️ حذف انتخاب‌ها",
                command=delete_selected,
                font=self.fonts['button'],
                bg=self.colors['danger'],
                fg='white',
                padx=15,
                pady=5).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(button_frame,
                text="❌ انصراف",
                command=dialog.destroy,
                font=self.fonts['button'],
                bg=self.colors['gray'],
                fg='white',
                padx=15,
                pady=5).pack(side=tk.RIGHT, padx=5)
        
    def update_user_telegram_chat_id(self, student_id, chat_id):
        """
        ثبت chat_id تلگرام برای کاربر
        (توسط ربات صدا زده می‌شود)
        """
        for user in self.users:
            if user.get('student_id') == student_id:
                user['telegram_chat_id'] = chat_id
                self.save_data()
                return True
        return False
    
    def send_telegram_for_selected_loan(self):
        """
        ارسال پیام تلگرام فقط برای امانت انتخاب‌شده در داشبورد
        """
        if not hasattr(self, 'dashboard_tree'):
            messagebox.showwarning("خطا", "داشبورد یادآوری باز نشده است.", parent=self.dashboard_dialog)
            return

        selection = self.dashboard_tree.selection()
        if not selection:
            messagebox.showwarning("خطا", "لطفاً یک امانت را از لیست انتخاب کنید.", parent=self.dashboard_dialog)
            return

        item = selection[0]
        values = self.dashboard_tree.item(item, 'values')

        borrower_name = values[0]
        borrower_id = values[1]
        book_title = values[2]
        borrow_date = values[3]
        return_date = values[4]

        # پیدا کردن کاربر
        user = None
        for u in self.users:
            if u.get('student_id') == borrower_id:
                user = u
                break

        if not user:
            messagebox.showerror("خطا", "کاربر مورد نظر یافت نشد.", parent=self.dashboard_dialog)
            return

        if not user.get('telegram_chat_id'):
            messagebox.showwarning(
                "تلگرام فعال نیست",
                "این کاربر هنوز ربات تلگرام را start نکرده است.",
                parent=self.dashboard_dialog
            )
            return

        try:
            from telegram_bot import send_loan_reminder
        except ImportError:
            messagebox.showerror(
                "خطا",
                "فایل telegram_bot.py یافت نشد.",
                parent=self.dashboard_dialog
            )
            return

        send_loan_reminder(
            chat_id=user['telegram_chat_id'],
            borrower_name=borrower_name,
            book_title=book_title,
            borrow_date=borrow_date,
            return_date=return_date
        )

        messagebox.showinfo(
            "ارسال شد",
            "پیام تلگرام با موفقیت ارسال شد.",
            parent=self.dashboard_dialog
        )



def main():
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()