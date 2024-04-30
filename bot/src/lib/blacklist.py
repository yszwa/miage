import re

async def overwrite(text: str):
    # コードブロックをコード省略に置き換える
    text = re.sub(r'```[\s\S]*?```', 'コード省略', text)
    # コードをコード省略に置き換える
    text = re.sub(r'`.*?`', 'コード省略', text)
    # URLをリンク省略に置き換える
    text = re.sub(r'https?://\S+', 'リンク省略', text)
    # メンションは省略
    text = re.sub(r'<@.*?>', '', text)
    # 絵文字は省略
    text = re.sub(r'<:.*?:.*?>', '', text)
    #アニメーション絵文字は省略
    text = re.sub(r'<a:.*?:.*?>', '', text)
    # ネタバレは省略
    text = re.sub(r'\|\|.*?\|\|', 'ネタバレ', text)
    # 特殊記号それぞれに読みを割り当てる
    text = re.sub(r'&', 'アンド', text)
    text = re.sub(r'＆', 'アンド', text)
    #その他の特殊な文字列は省略
    special_characters = "!@#$%^*()_-+=<>,./?;:'\"[]{}\\|`~"
    translate_table = str.maketrans('', '', special_characters)
    text = text.translate(translate_table)

    with open ('/app/src/lib/bep-eng.dic', 'r', encoding='utf-8') as f:
        bep_eng = sorted(f.read().split('\n'), key=len, reverse=True)
    for i in bep_eng:
        r = i.split(' ')
        text = text.upper().replace(r[0], r[1])

    # wが2文字以上の場合はわらわらに置き換える
    text = re.sub(r'W{2,}', 'わらわら', text)
    # wが1文字の場合はわらに置き換える
    text = re.sub(r'W', 'わら', text)
    #上2つを全角のｗにも適用
    text = re.sub(r'Ｗ{2,}', 'わらわら', text)
    text = re.sub(r'Ｗ', 'わら', text)

    return text
