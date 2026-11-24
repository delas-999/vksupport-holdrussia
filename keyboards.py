from vkbottle import Keyboard, Text, KeyboardButtonColor

def get_main_kb():
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text("❓ Частые вопросы"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("📩 Создать тикет"), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text("💥 Сообщить о баге"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("📂 Мои тикеты"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("❌ Закрыть тикет"), color=KeyboardButtonColor.NEGATIVE)
    return kb.get_json()
