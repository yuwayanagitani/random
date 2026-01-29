import os
import re
import random
import html

from aqt import gui_hooks, mw
from aqt.utils import openFolder, showInfo
from aqt.qt import (
    QAction,
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QCheckBox, QLineEdit, QSpinBox, QPushButton,
    QDialogButtonBox, QLabel, QWidget,
    qconnect,
)

# 対応する画像拡張子
VALID_EXT = (".png", ".jpg", ".jpeg", ".gif")

# 直前に表示したファイル名（avoid_repeat 用）
_last_filename = None

# Session state for interval gating
_question_seen_count = 0
_current_card_should_show_image = False


def _reset_session_state():
    """Reset the session counter when profile/collection changes."""
    global _question_seen_count, _current_card_should_show_image
    _question_seen_count = 0
    _current_card_should_show_image = False
    print("[RandomImageAddon] Session state reset.")


def _defaults() -> dict:
    return {
        "enabled": True,
        "show_on_question": True,
        "show_on_answer": True,
        "folder_name": "random_images",
        "max_width_percent": 80,
        "max_height_vh": 60,
        "avoid_repeat": True,
        "show_filename": True,
        "show_every_n_cards": 1,
    }


def get_config() -> dict:
    """config.json を取得。失敗時はデフォルトを返す。"""
    default = _defaults()
    try:
        cfg = mw.addonManager.getConfig(__name__)
        if not isinstance(cfg, dict):
            return default
        return {**default, **cfg}
    except Exception as e:
        print("[RandomImageAddon] Failed to load config:", e)
        return default


def _write_config(new_cfg: dict) -> None:
    """互換性を保ちつつ config を保存（未知キーは維持）。"""
    try:
        old = mw.addonManager.getConfig(__name__)
        if not isinstance(old, dict):
            old = {}
        merged = {**old, **new_cfg}  # 既存の未知キーは残しつつ、GUI項目だけ更新
        mw.addonManager.writeConfig(__name__, merged)
    except Exception as e:
        print("[RandomImageAddon] Failed to write config:", e)


def _sanitize_folder_name(name: str) -> str:
    """
    collection.media の「サブフォルダ名」として安全そうな形に寄せる。
    - 空は random_images
    - 絶対パス/上位参照っぽいものは拒否（元に戻す）
    """
    s = (name or "").strip()
    if not s:
        return "random_images"

    # Windows の \ を / に寄せる（見た目統一）
    s = s.replace("\\", "/")

    # 絶対パス/上位参照の簡易ブロック
    if s.startswith(("/", "~")) or ":" in s or ".." in s:
        showInfo("Invalid folder name. Please use a simple subfolder name, e.g. random_images")
        return "random_images"

    # 末尾の / を除去
    s = s.strip("/")

    if not s:
        return "random_images"
    return s


def _media_subfolder_path(folder_name: str) -> str | None:
    col = getattr(mw, "col", None)
    if not col:
        return None
    media_dir = col.media.dir()
    return os.path.join(media_dir, folder_name)


def open_images_folder(folder_name: str | None = None) -> None:
    """collection.media/<folder_name> を作成して開く"""
    if folder_name is None:
        cfg = get_config()
        folder_name = cfg.get("folder_name", "random_images")

    folder_name = _sanitize_folder_name(str(folder_name))
    path = _media_subfolder_path(folder_name)
    if not path:
        showInfo("No collection is open.")
        return

    os.makedirs(path, exist_ok=True)
    openFolder(path)


class RandomImageSettingsDialog(QDialog):
    """設定GUI（configキー互換性維持、Tools増やさない）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Random Image Settings")
        self.setMinimumWidth(480)

        cfg = get_config()

        root = QVBoxLayout(self)

        desc = QLabel(
            "Settings are saved to config.json.\n"
            "They apply the next time a card is shown."
        )
        desc.setWordWrap(True)
        root.addWidget(desc)

        form = QFormLayout()
        root.addLayout(form)

        # enabled
        self.cb_enabled = QCheckBox("Enable add-on")
        self.cb_enabled.setChecked(bool(cfg.get("enabled", True)))
        form.addRow(self.cb_enabled)

        # show_on_question / answer
        self.cb_q = QCheckBox("Show on Question side")
        self.cb_q.setChecked(bool(cfg.get("show_on_question", True)))
        form.addRow(self.cb_q)

        self.cb_a = QCheckBox("Show on Answer side")
        self.cb_a.setChecked(bool(cfg.get("show_on_answer", True)))
        form.addRow(self.cb_a)

        # folder_name + open button
        self.le_folder = QLineEdit(str(cfg.get("folder_name", "random_images")))
        self.le_folder.setPlaceholderText("random_images")

        btn_open = QPushButton("Open folder")
        qconnect(btn_open.clicked, self._on_open_folder)

        folder_row = QWidget()
        folder_layout = QHBoxLayout(folder_row)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_layout.addWidget(self.le_folder, 1)
        folder_layout.addWidget(btn_open)

        form.addRow("Image folder (inside collection.media)", folder_row)

        # max_width_percent
        self.sp_w = QSpinBox()
        self.sp_w.setRange(0, 100)  # 0 = no limit
        self.sp_w.setValue(int(cfg.get("max_width_percent", 80) or 0))
        self.sp_w.setSuffix(" %")
        form.addRow("Max width", self.sp_w)

        # max_height_vh
        self.sp_h = QSpinBox()
        self.sp_h.setRange(0, 200)  # 0 = no limit
        self.sp_h.setValue(int(cfg.get("max_height_vh", 60) or 0))
        self.sp_h.setSuffix(" vh")
        form.addRow("Max height", self.sp_h)

        # avoid_repeat
        self.cb_avoid = QCheckBox("Avoid showing the same image twice in a row")
        self.cb_avoid.setChecked(bool(cfg.get("avoid_repeat", True)))
        form.addRow(self.cb_avoid)

        # show_filename
        self.cb_fn = QCheckBox("Show filename caption")
        self.cb_fn.setChecked(bool(cfg.get("show_filename", True)))
        form.addRow(self.cb_fn)

        # show_every_n_cards
        self.sp_interval = QSpinBox()
        self.sp_interval.setRange(1, 9999)  # min=1 as per spec
        self.sp_interval.setValue(int(cfg.get("show_every_n_cards", 1)))
        interval_help = QLabel("Show every N cards (1 = every card)")
        interval_help.setWordWrap(True)
        form.addRow("Show every N cards", self.sp_interval)
        form.addRow("", interval_help)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        # Reset to defaults ボタン（Anki/PyQtの差異で StandardButton が無い場合もあるので自前で追加）
        btn_reset = QPushButton("Reset to defaults")
        buttons.addButton(btn_reset, QDialogButtonBox.ButtonRole.ResetRole)
        qconnect(btn_reset.clicked, self._on_reset)

        qconnect(buttons.accepted, self._on_ok)
        qconnect(buttons.rejected, self.reject)
        root.addWidget(buttons)

    def _on_open_folder(self):
        folder = _sanitize_folder_name(self.le_folder.text())
        self.le_folder.setText(folder)
        open_images_folder(folder)

    def _on_ok(self):
        folder = _sanitize_folder_name(self.le_folder.text())
        self.le_folder.setText(folder)

        new_cfg = {
            "enabled": bool(self.cb_enabled.isChecked()),
            "show_on_question": bool(self.cb_q.isChecked()),
            "show_on_answer": bool(self.cb_a.isChecked()),
            "folder_name": folder,
            "max_width_percent": int(self.sp_w.value()),
            "max_height_vh": int(self.sp_h.value()),
            "avoid_repeat": bool(self.cb_avoid.isChecked()),
            "show_filename": bool(self.cb_fn.isChecked()),
            "show_every_n_cards": int(self.sp_interval.value()),
        }
        _write_config(new_cfg)
        self.accept()

    def _on_reset(self):
        d = _defaults()

        self.cb_enabled.setChecked(bool(d.get("enabled", True)))
        self.cb_q.setChecked(bool(d.get("show_on_question", True)))
        self.cb_a.setChecked(bool(d.get("show_on_answer", True)))

        self.le_folder.setText(str(d.get("folder_name", "random_images")))

        self.sp_w.setValue(int(d.get("max_width_percent", 80) or 0))
        self.sp_h.setValue(int(d.get("max_height_vh", 60) or 0))

        self.cb_avoid.setChecked(bool(d.get("avoid_repeat", True)))
        self.cb_fn.setChecked(bool(d.get("show_filename", True)))
        
        self.sp_interval.setValue(int(d.get("show_every_n_cards", 1)))



def open_settings_dialog(*args, **kwargs):
    """
    Add-ons画面の「Config」からも呼ばれる想定。
    呼び方が違っても動くように *args/**kwargs で受ける。
    """
    parent = kwargs.get("parent", None)
    if parent is None and args:
        parent = args[0]
    parent = parent or mw

    dlg = RandomImageSettingsDialog(parent=parent)
    dlg.exec()


def pick_random_image_filename(cfg: dict):
    """collection.media/<folder_name>/ からランダムなファイル名を返す。なければ None。"""
    global _last_filename
    try:
        col = getattr(mw, "col", None)
        if not col:
            return None

        folder_name = _sanitize_folder_name(cfg.get("folder_name", "random_images"))
        image_folder = _media_subfolder_path(folder_name)
        if not image_folder:
            return None

        if not os.path.isdir(image_folder):
            # フォルダがないなら「画像なし」扱い（勝手に作らない）
            return None

        files = [f for f in os.listdir(image_folder) if f.lower().endswith(VALID_EXT)]
        if not files:
            return None

        if cfg.get("avoid_repeat", True) and len(files) > 1:
            candidates = [f for f in files if f != _last_filename]
            if candidates:
                files = candidates

        filename = random.choice(files)
        _last_filename = filename
        return filename
    except Exception as e:
        print("[RandomImageAddon] Error while picking image:", e)
        return None


def inject_random_image(text: str, card, kind: str) -> str:
    """
    card_will_show フック用
    kind: "reviewQuestion", "reviewAnswer" など
    """
    global _question_seen_count, _current_card_should_show_image
    
    cfg = get_config()

    if not cfg.get("enabled", True):
        return text

    # Get interval setting with robust coercion
    interval = cfg.get("show_every_n_cards", 1)
    try:
        interval = int(interval)
        if interval <= 0:
            interval = 1
    except (TypeError, ValueError):
        interval = 1

    # Handle Question side: increment counter and decide if this card should show image
    if kind.endswith("Question"):
        _question_seen_count += 1
        _current_card_should_show_image = (_question_seen_count % interval == 0)
        
        # If this card should not show images, return early
        if not _current_card_should_show_image:
            return text
            
        if not cfg.get("show_on_question", True):
            return text
    elif kind.endswith("Answer"):
        # For Answer side, only show if the Question side decided to show
        if not _current_card_should_show_image:
            return text
            
        if not cfg.get("show_on_answer", True):
            return text
    else:
        # For other card kinds (unlikely in normal usage), don't show images
        # to avoid confusion from stale state
        return text

    filename = pick_random_image_filename(cfg)
    if not filename:
        return text

    folder_name = _sanitize_folder_name(cfg.get("folder_name", "random_images"))
    img_src = f"{folder_name}/{filename}"

    # Hover tooltip: show original filename (escape for HTML attribute safety)
    title_attr = html.escape(filename, quote=True)

    max_w = cfg.get("max_width_percent", 80)
    max_h = cfg.get("max_height_vh", 60)

    style_parts = []
    if isinstance(max_w, (int, float)) and max_w > 0:
        style_parts.append(f"max-width:{max_w}%")
    if isinstance(max_h, (int, float)) and max_h > 0:
        style_parts.append(f"max-height:{max_h}vh")
    style_parts.append("border-radius:8px")

    style_attr = "; ".join(style_parts)

    caption_html = ""
    if cfg.get("show_filename", True):
        base_name = os.path.splitext(filename)[0]
        base_name = base_name.replace("-", " ").replace("_", " ")
        base_name = re.sub(r"\d+", "", base_name)
        base_name = re.sub(r"\s+", " ", base_name).strip()
        base_name = base_name.upper()

        caption_html = f"""
  <div style="margin-top:6px; font-size:0.9em; color:#888;">
    {base_name}
  </div>
"""

    extra_html = f"""
<div style="text-align:center; margin-top:15px;">
  <img src="{img_src}" style="{style_attr}" title="{title_attr}">
{caption_html}</div>
"""
    return text + extra_html


def _register_config_action() -> None:
    """
    Add-ons画面の「Config」ボタン → このGUIを開く
    """
    try:
        mw.addonManager.setConfigAction(__name__, open_settings_dialog)
        print("[RandomImageAddon] Config action registered.")
    except Exception as e:
        # 古いAnki等でAPIが無い場合のみ、最終手段として Tools に出す（通常は出ない）
        print("[RandomImageAddon] setConfigAction not available:", e)
        try:
            menu = getattr(mw.form, "menuTools", None) or getattr(mw.form, "toolsMenu", None)
            if menu is not None:
                act = QAction("Random Image Settings…", mw)
                qconnect(act.triggered, open_settings_dialog)
                menu.addAction(act)
        except Exception as e2:
            print("[RandomImageAddon] Fallback menu failed:", e2)


def _on_main_window_init():
    _register_config_action()
    # Reset session state when profile/collection changes
    gui_hooks.profile_did_open.append(_reset_session_state)
    gui_hooks.collection_did_load.append(lambda col: _reset_session_state())


# メインウィンドウ初期化後に登録
gui_hooks.main_window_did_init.append(_on_main_window_init)

# カード表示時のフック
gui_hooks.card_will_show.append(inject_random_image)
