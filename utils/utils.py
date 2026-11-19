"""操作员账户存储（本地 CSV，演示环境使用）。"""
from __future__ import annotations

import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "user_data.csv"


def _ensure_file() -> None:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["admin", "admin"])


def get_user_data() -> dict[str, str]:
    """读取全部操作员账户，返回 {账号: 密码}。"""
    _ensure_file()
    users: dict[str, str] = {}
    with DATA_FILE.open("r", newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0].strip():
                users[row[0].strip()] = row[1].strip()
    return users


def update_user_data(user_id: str, user_name: str) -> None:
    """新增操作员账户。"""
    _ensure_file()
    with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([user_id, user_name])
