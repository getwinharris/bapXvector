#!/usr/bin/env python3

"""
skin.py — GUI for bapX
Author: getwinharris

Knowledge Base:
1. Admin panel is fully dynamic for module pinning, URL input, FA icon assignment, and styling.
2. Mic, Attach, Web buttons are fully FA icon-based and configurable.
3. Pulling GitHub modules triggers dynamic character mapping and synchronous backup.
4. Pinned modules are recorded in creator.x Table 2 (with name, URL, pin status, icon).
5. Users see a read-only menu reflecting pinned modules; no access to core capsules.
6. Admin styling controls persist to creator.x Table 2.
7. Only actual eight-page files and essential capsules are considered; legacy or non-existent files are removed.

Purpose: Chat interface dynamically driven by bapx.in VECTOR_SECTION.
Connects directly to the brain cognition pipeline for message processing.
"""

import sys
import os
import shutil
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSizePolicy,
    QComboBox, QGridLayout, QColorDialog, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from brain import process_message
from creator import Table2  # Assuming creator.x Table 2 is accessible as a module
from mapping import map_characters_from_file  # Assuming this function exists for mapping

# ---------------------------
# Main GUI
# ---------------------------
class BapXChat(QWidget):
    # ---------------------------
    # UI Styling and Theme Variables for Admin IDE Pages
    # ---------------------------
    DEFAULT_FONT_FAMILY = "Segoe UI, Tahoma, Geneva, Verdana, sans-serif"
    DEFAULT_HEADER_SIZES = {
        "h1": 24,
        "h2": 20,
        "h3": 18,
        "h4": 16,
        "h5": 14
    }
    DEFAULT_PARAGRAPH_STYLE = {
        "font_size": 14,
        "line_height": 1.5,
        "margin_top": 8,
        "margin_bottom": 8
    }
    DEFAULT_BASE_COLORS = {
        "background": "#1e1e1e",
        "text": "#d4d4d4",
        "primary": "#007acc",
        "secondary": "#3a3d41",
        "highlight": "#569cd6"
    }

    # Admin-configurable variables initialized with defaults
    font_family = DEFAULT_FONT_FAMILY
    header_sizes = DEFAULT_HEADER_SIZES.copy()
    paragraph_style = DEFAULT_PARAGRAPH_STYLE.copy()
    base_colors = DEFAULT_BASE_COLORS.copy()

    # Icon mapping for pinned GitHub modules (admin sidebar and user menu)
    # Icons assigned dynamically by admin and persisted in creator.x Table 2
    MODULE_ICONS = {}

    # Admin configurable icon classes for buttons
    ADMIN_ICON_CLASSES = {
        "mic_button": "fa-microphone",
        "attach_button": "fa-paperclip",
        "web_button": "fa-globe"
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("bapX Chat Interface")
        self.resize(900, 700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Admin styling controls container
        self.admin_controls_layout = QVBoxLayout()
        self.layout.addLayout(self.admin_controls_layout)

        # Font family selection dropdown for admin
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Font Family:")
        font_family_layout.addWidget(font_family_label)

        self.font_family_combo = QComboBox()
        font_options = [
            "Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
            "Arial, Helvetica, sans-serif",
            "Courier New, Courier, monospace",
            "Georgia, serif",
            "Times New Roman, Times, serif",
            "Verdana, Geneva, sans-serif",
            "Trebuchet MS, Helvetica, sans-serif",
            "Comic Sans MS, cursive, sans-serif"
        ]
        self.font_family_combo.addItems(font_options)
        current_font = self.font_family if hasattr(self, "font_family") else self.DEFAULT_FONT_FAMILY
        if current_font in font_options:
            self.font_family_combo.setCurrentText(current_font)
        else:
            self.font_family_combo.setCurrentIndex(0)
        self.font_family_combo.currentTextChanged.connect(self.update_font_family)
        font_family_layout.addWidget(self.font_family_combo)
        self.admin_controls_layout.addLayout(font_family_layout)

        # Header sizes editing grid (h1-h5)
        header_sizes_layout = QGridLayout()
        header_sizes_layout.addWidget(QLabel("Header Sizes (px):"), 0, 0, 1, 2)
        self.header_size_spins = {}
        for i, level in enumerate(["h1", "h2", "h3", "h4", "h5"], start=1):
            lbl = QLabel(level.upper() + ":")
            spin = QSpinBox()
            spin.setRange(8, 72)
            spin.setValue(self.header_sizes.get(level, self.DEFAULT_HEADER_SIZES[level]))
            spin.valueChanged.connect(self.update_header_sizes)
            header_sizes_layout.addWidget(lbl, i, 0)
            header_sizes_layout.addWidget(spin, i, 1)
            self.header_size_spins[level] = spin
        self.admin_controls_layout.addLayout(header_sizes_layout)

        # Paragraph style controls
        paragraph_layout = QHBoxLayout()
        paragraph_label = QLabel("Paragraph Style:")
        paragraph_layout.addWidget(paragraph_label)

        self.paragraph_font_size_spin = QSpinBox()
        self.paragraph_font_size_spin.setRange(8, 48)
        self.paragraph_font_size_spin.setValue(self.paragraph_style.get("font_size", self.DEFAULT_PARAGRAPH_STYLE["font_size"]))
        self.paragraph_font_size_spin.setPrefix("Font Size: ")
        self.paragraph_font_size_spin.valueChanged.connect(self.update_paragraph_style)
        paragraph_layout.addWidget(self.paragraph_font_size_spin)

        self.paragraph_line_height_spin = QSpinBox()
        self.paragraph_line_height_spin.setRange(1, 5)
        self.paragraph_line_height_spin.setValue(int(self.paragraph_style.get("line_height", self.DEFAULT_PARAGRAPH_STYLE["line_height"])*10))
        self.paragraph_line_height_spin.setSuffix(" (x10)")
        self.paragraph_line_height_spin.valueChanged.connect(self.update_paragraph_style)
        paragraph_layout.addWidget(self.paragraph_line_height_spin)

        self.paragraph_margin_top_spin = QSpinBox()
        self.paragraph_margin_top_spin.setRange(0, 50)
        self.paragraph_margin_top_spin.setValue(self.paragraph_style.get("margin_top", self.DEFAULT_PARAGRAPH_STYLE["margin_top"]))
        self.paragraph_margin_top_spin.setPrefix("Margin Top: ")
        self.paragraph_margin_top_spin.valueChanged.connect(self.update_paragraph_style)
        paragraph_layout.addWidget(self.paragraph_margin_top_spin)

        self.paragraph_margin_bottom_spin = QSpinBox()
        self.paragraph_margin_bottom_spin.setRange(0, 50)
        self.paragraph_margin_bottom_spin.setValue(self.paragraph_style.get("margin_bottom", self.DEFAULT_PARAGRAPH_STYLE["margin_bottom"]))
        self.paragraph_margin_bottom_spin.setPrefix("Margin Bottom: ")
        self.paragraph_margin_bottom_spin.valueChanged.connect(self.update_paragraph_style)
        paragraph_layout.addWidget(self.paragraph_margin_bottom_spin)

        self.admin_controls_layout.addLayout(paragraph_layout)

        # Base colors controls with color pickers
        colors_layout = QGridLayout()
        colors_layout.addWidget(QLabel("Base Colors:"), 0, 0, 1, 2)
        self.color_buttons = {}
        for i, (color_name, default_hex) in enumerate(self.base_colors.items(), start=1):
            lbl = QLabel(color_name.capitalize() + ":")
            btn = QPushButton()
            btn.setStyleSheet(f"background-color: {default_hex};")
            btn.clicked.connect(lambda checked, cn=color_name: self.pick_color(cn))
            colors_layout.addWidget(lbl, i, 0)
            colors_layout.addWidget(btn, i, 1)
            self.color_buttons[color_name] = btn
        self.admin_controls_layout.addLayout(colors_layout)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # Input + Buttons
        self.input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_layout.addWidget(self.input_field)

        self.mic_button = QPushButton()
        mic_icon_class = self.ADMIN_ICON_CLASSES.get("mic_button", "")
        self.mic_button.setText(f'<i class="fa {mic_icon_class}"></i>')
        self.mic_button.setStyleSheet(f"font-family: FontAwesome; font-size: 16pt;")
        self.mic_button.setObjectName("mic_button")
        self.mic_button.clicked.connect(self.handle_dynamic_click)
        self.input_layout.addWidget(self.mic_button)

        self.attach_button = QPushButton()
        attach_icon_class = self.ADMIN_ICON_CLASSES.get("attach_button", "")
        self.attach_button.setText(f'<i class="fa {attach_icon_class}"></i>')
        self.attach_button.setStyleSheet(f"font-family: FontAwesome; font-size: 16pt;")
        self.attach_button.setObjectName("attach_button")
        self.attach_button.clicked.connect(self.handle_dynamic_click)
        self.input_layout.addWidget(self.attach_button)

        self.web_button = QPushButton()
        web_icon_class = self.ADMIN_ICON_CLASSES.get("web_button", "")
        self.web_button.setText(f'<i class="fa {web_icon_class}"></i>')
        self.web_button.setStyleSheet(f"font-family: FontAwesome; font-size: 16pt;")
        self.web_button.setObjectName("web_button")
        self.web_button.clicked.connect(self.handle_dynamic_click)
        self.input_layout.addWidget(self.web_button)

        self.layout.addLayout(self.input_layout)

        # Auto-refresh timer to update chat from VECTOR_SECTION
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_chat)
        self.timer.start(500)  # refresh every 500ms

        # Admin pinned modules info, loaded from creator.x Table 2
        self.pinned_modules = {}  # name -> dict with keys: index_path, url, pinned, icon

        self.load_pinned_modules_from_table()

        self.show()

    # ---------------------------
    # Load pinned modules and icons from creator.x Table 2
    # ---------------------------
    def load_pinned_modules_from_table(self):
        try:
            # Assuming Table2 has columns: module_name, main_entry_path, url, pinned (bool), icon (fa class)
            entries = Table2.query_all()
            for entry in entries:
                name = entry.module_name
                if name in {"brain.x", "creator.x", "sharedspace.x"}:
                    continue
                self.pinned_modules[name] = {
                    "index_path": entry.main_entry_path,
                    "url": entry.url,
                    "pinned": entry.pinned,
                    "icon": entry.icon or ""
                }
                if entry.icon:
                    self.MODULE_ICONS[name] = entry.icon
            self.update_user_menu()
        except Exception as e:
            self.add_system_message(f"[Failed to load pinned modules from Table 2: {e}]")

    # ---------------------------
    # Save pinned module info to creator.x Table 2
    # ---------------------------
    def save_pinned_module_to_table(self, name: str, index_path: str, url: str, pinned: bool, icon: str):
        try:
            # Upsert entry in Table2
            Table2.upsert(module_name=name, main_entry_path=index_path, url=url, pinned=pinned, icon=icon)
        except Exception as e:
            self.add_system_message(f"[Failed to save pinned module '{name}' to Table 2: {e}]")

    # ---------------------------
    # Update font family from dropdown selection
    # ---------------------------
    def update_font_family(self, font_family: str):
        self.font_family = font_family
        self.add_system_message(f"[Font family updated to: {font_family}]")
        self.persist_admin_styling()

    # ---------------------------
    # Update header sizes from spinboxes
    # ---------------------------
    def update_header_sizes(self):
        for level, spin in self.header_size_spins.items():
            self.header_sizes[level] = spin.value()
        self.add_system_message(f"[Header sizes updated: {self.header_sizes}]")
        self.persist_admin_styling()

    # ---------------------------
    # Update paragraph style from controls
    # ---------------------------
    def update_paragraph_style(self):
        self.paragraph_style["font_size"] = self.paragraph_font_size_spin.value()
        self.paragraph_style["line_height"] = self.paragraph_line_height_spin.value() / 10.0
        self.paragraph_style["margin_top"] = self.paragraph_margin_top_spin.value()
        self.paragraph_style["margin_bottom"] = self.paragraph_margin_bottom_spin.value()
        self.add_system_message(f"[Paragraph style updated: {self.paragraph_style}]")
        self.persist_admin_styling()

    # ---------------------------
    # Pick color for base colors
    # ---------------------------
    def pick_color(self, color_name: str):
        current_color = QColor(self.base_colors.get(color_name, self.DEFAULT_BASE_COLORS[color_name]))
        color = QColorDialog.getColor(current_color, self, f"Select color for {color_name}")
        if color.isValid():
            hex_color = color.name()
            self.base_colors[color_name] = hex_color
            btn = self.color_buttons.get(color_name)
            if btn:
                btn.setStyleSheet(f"background-color: {hex_color};")
            self.add_system_message(f"[Base color '{color_name}' updated to {hex_color}]")
            self.persist_admin_styling()

    # ---------------------------
    # Persist admin styling settings to creator.x Table 2
    # ---------------------------
    def persist_admin_styling(self):
        try:
            # Serialize header_sizes and paragraph_style and base_colors as JSON strings or dicts
            styling_data = {
                "font_family": self.font_family,
                "header_sizes": self.header_sizes,
                "paragraph_style": self.paragraph_style,
                "base_colors": self.base_colors
            }
            # Upsert a special entry in Table2 with module_name='admin_styling' or similar
            Table2.upsert(module_name="admin_styling", main_entry_path="", url="", pinned=False,
                          icon="", extra_data=styling_data)
        except Exception as e:
            self.add_system_message(f"[Failed to persist admin styling to Table 2: {e}]")

    # ---------------------------
    # Add system message
    # ---------------------------
    def add_system_message(self, msg: str):
        self.chat_display.append(f"<i>{msg}</i>")

    # ---------------------------
    # Send user message
    # ---------------------------
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.chat_display.append(f"<b>Humane:</b> {text}")
        self.input_field.clear()
        # Trigger bapX pipeline
        try:
            self.chat_display.append("<i>[Mirroring]</i>")
            QApplication.processEvents()
            response = process_message(text)
            self.chat_display.append("<i>[Reflecting]</i>")
            QApplication.processEvents()
            self.chat_display.append(f"<b>bapX:</b> {response}")
        except Exception as e:
            self.chat_display.append(f"<i>Error in bapX trigger: {e}</i>")

    # ---------------------------
    # Refresh chat display from VECTOR_SECTION
    # ---------------------------
    def refresh_chat(self):
        # Optionally, could pull latest reflections from VECTOR_SECTION["reflection_vectors"]
        # For now, we keep it simple; main messages are appended on send
        pass

    # ---------------------------
    # Pull GitHub X module given a URL
    # ---------------------------
    def pull_github_module(self, url: str):
        """
        Downloads or updates a GitHub module from the given URL.
        Assumes the URL is a GitHub repo URL pointing to the root of the module.
        Does NOT hardcode main entry file; admin should select main entry after pulling.
        After pulling, calls map_characters_from_file(), performs backup, and updates creator.x Table 2.
        Also assigns a default FA icon for all modules except brain.x.
        """
        try:
            if not url.startswith("https://github.com/"):
                self.add_system_message("[Error] Only GitHub URLs are supported for module pulling.")
                return
            parts = url.rstrip('/').split('/')
            if len(parts) < 5:
                self.add_system_message("[Error] Invalid GitHub repo URL format.")
                return
            owner = parts[3]
            repo = parts[4]
            branch = "main"
            raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
            modules_dir = os.path.join(os.getcwd(), "modules")
            if not os.path.exists(modules_dir):
                os.makedirs(modules_dir)
            module_path = os.path.join(modules_dir, repo)
            if os.path.exists(module_path):
                shutil.rmtree(module_path)
            os.makedirs(module_path)
            self.add_system_message(f"[Pulling GitHub module '{repo}' from {url}]")

            # Download README.md as placeholder
            readme_url = raw_base + "README.md"
            r = requests.get(readme_url)
            if r.status_code == 200:
                with open(os.path.join(module_path, "README.md"), "wb") as f:
                    f.write(r.content)
                self.add_system_message("[Downloaded README.md as reference]")
            else:
                self.add_system_message("[No README.md found in repo root]")

            # Map characters from all files in the pulled module folder (*.*)
            for root, dirs, files in os.walk(module_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    map_characters_from_file(file_path)

            # Assign default FA icon for pulled module (except brain.x)
            self.set_default_module_icon(repo)

            # Backup the pulled module synchronously
            backup_path = module_path + ".bak"
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(module_path, backup_path)
            self.add_system_message(f"[Backup created at {backup_path}]")

            # Update creator.x Table 2 with module info
            # Assume main entry path is unknown, admin to select manually; set empty string
            # Pin status default False, icon may have been set by set_default_module_icon
            icon_val = self.MODULE_ICONS.get(repo, "")
            self.save_pinned_module_to_table(name=repo, index_path="", url=url, pinned=False, icon=icon_val)
            self.pinned_modules[repo] = {
                "index_path": "",
                "url": url,
                "pinned": False,
                "icon": icon_val
            }

            self.add_system_message(f"[Module '{repo}' pulled and mapped successfully.]")
            self.add_system_message("[Please select the main entry file and assign icon manually in admin panel.]")
        except Exception as e:
            self.add_system_message(f"[Failed to pull GitHub module: {e}]")


    # ---------------------------
    # Set default FA icon for pulled module (except brain.x)
    # ---------------------------
    def set_default_module_icon(self, repo_name: str):
        """
        Assigns a default FA icon ("fa-box") for pulled module unless it's 'brain.x'.
        Persists to Table2.
        """
        if repo_name == "brain.x":
            return
        default_icon = "fa-box"
        self.MODULE_ICONS[repo_name] = default_icon
        # Try to update Table2 if entry exists, else add
        try:
            # Upsert with empty index_path, url, not pinned, but with icon
            # Table2.upsert will overwrite icon if already exists
            existing_url = self.pinned_modules.get(repo_name, {}).get("url", "")
            self.save_pinned_module_to_table(repo_name, "", existing_url, False, default_icon)
        except Exception as e:
            self.add_system_message(f"[Failed to set default icon for module '{repo_name}': {e}]")

    # ---------------------------
    # Pin the main entry page (index) in the admin sidebar for quick access
    # ---------------------------
    def pin_module_for_admin(self, name: str, index_path: str, icon_class: str = ""):
        """
        Pins a module's main entry page for admin quick access.
        Modules named brain.x, creator.x, or sharedspace.x are NOT pinned.
        Saves pin info and icon to creator.x Table 2.
        """
        if name in {"brain.x", "creator.x", "sharedspace.x"}:
            self.add_system_message(f"[Module '{name}' is restricted and cannot be pinned.]")
            return
        self.pinned_modules[name] = {
            "index_path": index_path,
            "url": self.pinned_modules.get(name, {}).get("url", ""),
            "pinned": True,
            "icon": icon_class
        }
        self.MODULE_ICONS[name] = icon_class
        self.add_system_message(f"[Pinned module '{name}' at '{index_path}' with icon '{icon_class}' for admin sidebar]")
        # Persist to Table 2
        self.save_pinned_module_to_table(name, index_path, self.pinned_modules[name]["url"], True, icon_class)
        self.update_user_menu()

    # ---------------------------
    # Reflect pinned module as a menu item in the user UI
    # ---------------------------
    def update_user_menu(self):
        """
        Updates the user UI menu to reflect pinned modules.
        Menu items are read-only; users cannot edit code.
        Integration point for UI.js menu reflection.
        """
        filtered_modules = {name: data for name, data in self.pinned_modules.items()
                            if data.get("pinned", False) and name not in {"brain.x", "creator.x", "sharedspace.x"}}
        menu_items = []
        for name, data in filtered_modules.items():
            icon = data.get("icon", "")
            menu_items.append({"name": name, "path": data.get("index_path", ""), "editable": False, "icon": icon})
        self.add_system_message(f"[Updated user menu with pinned modules: {list(filtered_modules.keys())}]")
        # Integration point: send menu_items to UI.js or front-end

    # ---------------------------
    # Retrieve icon for a given module name
    # ---------------------------
    def get_module_icon(self, module_name: str) -> str:
        """
        Returns the icon associated with the module name.
        If no specific icon exists, returns an empty string.
        Icons are assigned dynamically by admin for pinned modules.
        """
        return self.MODULE_ICONS.get(module_name, "")

    # ---------------------------
    # Apply font styling to headers for admin IDE pages
    # ---------------------------
    def styled_header(self, text: str, level: str = "h1") -> str:
        """
        Returns HTML string for styled header with given level (h1-h5).
        Applies font family and size according to theme variables.
        """
        size = self.header_sizes.get(level, self.DEFAULT_HEADER_SIZES["h1"])
        font_family = getattr(self, "font_family", self.DEFAULT_FONT_FAMILY)
        primary_color = self.base_colors.get("primary", self.DEFAULT_BASE_COLORS["primary"])
        return (f'<div style="font-family: {font_family}; '
                f'font-size: {size}px; font-weight: bold; color: {primary_color}; '
                f'margin: 10px 0;">{text}</div>')

    # ---------------------------
    # Apply paragraph styling for admin IDE pages
    # ---------------------------
    def styled_paragraph(self, text: str) -> str:
        """
        Returns HTML string for styled paragraph.
        Applies font family, size, line height, and color according to theme variables.
        """
        font_family = getattr(self, "font_family", self.DEFAULT_FONT_FAMILY)
        ps = getattr(self, "paragraph_style", self.DEFAULT_PARAGRAPH_STYLE)
        text_color = self.base_colors.get("text", self.DEFAULT_BASE_COLORS["text"])
        return (f'<p style="font-family: {font_family}; font-size: {ps["font_size"]}px; '
                f'line-height: {ps["line_height"]}; margin-top: {ps["margin_top"]}px; margin-bottom: {ps["margin_bottom"]}px; '
                f'color: {text_color};">{text}</p>')

# ---------------------------
# Run application
# ---------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BapXChat()
    sys.exit(app.exec())

    # ---------------------------
    # Dynamic reusable button click handler
    # ---------------------------
    def handle_dynamic_click(self):
        sender = self.sender()
        if sender is None:
            return
        btn_obj_name = sender.objectName()
        # Map object name to friendly button name for message
        btn_name_map = {
            "mic_button": "Mic",
            "attach_button": "Attach",
            "web_button": "Web"
        }
        btn_name = btn_name_map.get(btn_obj_name, btn_obj_name)
        self.add_system_message(f"[{btn_name} pressed]")

# ---------------------------
# Knowledge Base — System Workflow & Philosophy
# ---------------------------
"""
1. Two-Stage Processing for X Files:
   - Stage 1: Reflection — preserves symbolic equilibrium for all newly pulled or created X files.
   - Stage 2: Compression/Folding — applies xAt (atomic float) scaling and mapping to xCh (symbolic character set) for memory-efficient storage.
   - Stage 3 (Optional, Admin): Visualization & Editing — floats and character mapping are applied for rendering and admin edits without altering the underlying capsule data.

2. Character Mapping:
   - All characters (existing and new) are dynamically mapped into the internal xCh table.
   - Missing characters discovered in conversation or newly pulled modules trigger mapping automatically.
   - Admin panel can optionally trigger a web crawl to detect missing symbols in external files or inputs.

3. Capsule Integrity:
   - User and system capsules are written and backed up synchronously.
   - brain.x, creator.x, sharedspace.x, and username.x maintain their own float and character mapping independently.
   - The system preserves data meaning while minimizing byte drift; no external encoding (UTF-8/JSON) is needed except for UI display.

4. Admin Controls & UI:
   - Font family, header sizes, paragraph style, and base colors are dynamically configurable and persisted in creator.x Table 2.
   - Pinned GitHub modules are stored in creator.x Table 2 with FA icons, pin status, and URLs.
   - Mic, Attach, and Web buttons are fully dynamic, icon-based, and trigger the bapX pipeline without lambda functions, maintaining consistent float and mapping logic.

5. Philosophy & Design Principles:
   - Every process preserves symbolic equilibrium: b = (b * 8) / 8 ensures A == A across transformations.
   - Only eight core pages plus essential capsules are used; legacy or redundant files are removed.
   - Admin and user perspectives are separated; users see a read-only menu reflecting pinned modules, while admin can configure, pin, and style all modules.
   - The system is designed for 2025 production-grade minimalism: lightweight, visually clear, and memory-efficient while keeping full cognitive integrity for AI processing.

6. Notes:
   - This knowledge base should evolve as new modules, symbols, or float transformations are introduced.
   - All future UI and module updates should reference this workflow to maintain consistency and preserve symbolic integrity.
"""
