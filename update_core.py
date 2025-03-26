
import urllib.request
import os

def update_core_script():
    url = "https://github.com/Pankhnnatan/autocaller/blob/main/autocaller_core.py"
    local_path = "autocaller_core.py"

    try:
        print("🔄 Проверка обновлений autocaller_core.py...")
        urllib.request.urlretrieve(url, local_path)
        print("✅ autocaller_core.py обновлён.")
    except Exception as e:
        print(f"⚠️ Не удалось обновить autocaller_core.py: {e}")
