from pathlib import Path

path = Path("apps/api/services/model_service.py")
text = path.read_text(encoding="utf-8")

text = text.replace('"mean_age": round(m_age, 1),', '"mean_age": round(m_age, 2),')
text = text.replace('"commercial_office_share_pct": round(off_share, 1),', '"commercial_office_share_pct": round(off_share, 2),')
text = text.replace('"commercial_office_share_pct": round(off_sh, 1),', '"commercial_office_share_pct": round(off_sh, 2),')

path.write_text(text, encoding="utf-8")
print("Updated rounding in model_service.py")
