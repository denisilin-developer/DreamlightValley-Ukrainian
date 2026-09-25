# usage: final_unify.py <batch dir>   → writes <batch dir>/out/zz_final.jsonl (sorts last, overrides)
# Applies the one-form-per-name decisions collected in pending_fixes.txt to every A/B output line,
# then reports how many lines each rule touched. Only whole-name variants — no free-text rewording.
import sys, json, glob, re, collections, pathlib

b = pathlib.Path(sys.argv[1])
SUBS = [
    # (regex, replacement) — case endings kept where the variant declines the same way
    (r"\bПутін\w*", "канадська картопля з сиром"),
    (r"«?Стічн(а|ої|у|ою) мод(а|и|у|ою)»?", "«Мода від Стіча»"),
    (r"Бармаглот|Бурмоглот", "Джабервок"),
    (r"Пам'ятн(а|ої|у|ою) річ(чю|і)?\b", "Пам'ятка"),
    (r"Сторінк(а|и|у|ою) з Журналу", r"Сторінк\1 зі Щоденника"),
    (r"\bВаян(а|и|і|у|ою)\b", r"Моан\1"),
    (r"Почати квест", "Почати завдання"), (r"Розпочати квест", "Розпочати завдання"),
    (r"Колон(а|и|і|у|ою) Турботи", r"Колон\1 Плекання"),
    (r"\bЗефірк(о|а|ові|ом|у)\b", r"Зефірчик"),
    (r"Жуйкоп'ятк\w*", "Жуйкопуз"), (r"М'ятокрутик\w*", "М'ятноніс"),
    (r"Сюжетн(а|ої|у|ою) бур(я|і|ю|ею)", "Сюжетний смерч"),
    (r"Прядк(а|и|у|ою) снів", "Веретено мрій"),
    (r"«Серденько!»", "«Золотко!»"),
    (r"НА ПОМІЧ", "НА ДОПОМОГУ"),
    (r"Пан(а|ові|ом|е)? Лисик(а|ові|ом|у)?", r"Містер Лисик\2"),
    (r"Ненажерлив(ий|ого|ому|им) Кабан(а|ові|ом)?", r"Ненажерлив\1 Вепр\2"),
    (r"Місячн(а|ої|у|ою) пов'язк(а|и|у|ою)", "Місячний обідок"),
    (r"Запасн(ий|ого|ому|им) п'ятачок(ка|ком)?", r"Запасн\1 ніс"),
    (r"Таємн(ий|ого|ому|им) журнал(у|ом)?", r"Таємн\1 щоденник\2"),
    (r"Перекоти-спагеті", "Спагеті-перекотиполе"),
    (r"Гігітус-Фігітус", "Хігітус Фігітус"),
    (r"\bСлінкі\b", "Пружинка"),
    (r"буньюелос|Буньюелос", "буньєлос"),
    (r"Блискуч(а|ої|у|ою) вудк(а|и|у|ою)", r"Іскрист\1 вудк\2"),
    (r"Чай з бульбашками|чай з бульбашками", "бабл-ті"),
    (r"\bТОКМ\b", "ТККМ"),
    (r"Вибий гарбуза", "Прибий гарбуза"), (r"привиденят(а|ам|ами|ах)?", "привидики"),
    (r"Юшк(а|и|у|ою) зі змій і павуків", "рагу зі змій і павуків"),
    (r"Світн(і|их|ими) водорост(і|ей|ями)", r"Сяйлив\1 водорост\2"),
    (r"«?Цукровий шал»?", "«Цукровий форсаж»"),
    (r"[Кк]омпостн(ий|ого|ому|им) контейнер(а|у|ом)?", "компостер"),
    (r"Будівництв(о|а|у|ом) Макдака", "«Макдак-Буд»"),
    (r"Подорож(і|ю)? астронома", "Шлях астронома"),
    (r"Бігунчик", "Метушунчик"), (r"Порхунчик", "Пурхунчик"),
    (r"Солодощі або (лихо|страхіття|пустощі)", "Солодощі або капость"),
    (r"ВАЛЛ·І", "ВОЛЛ·І"), (r"^Гей, спокійніше", "Агов, спокійніше"),
    (r"Крутокор(інь|ені|енів|енями|еня)", lambda m: "кручекор"+m.group(1)),
    (r"Богом'ятник\w*", "«Богом'ята»"),
    (r"\bHola\b", "Ола"), (r"Muchas gracias", "Мучас ґрасіас"), (r"De nada", "Де нада"),
    (r"Bon appétit", "Бон апетит"), (r"Merci beaucoup", "Мерсі боку"), (r"\bmagnifique\b", "маніфік"),
]
# rules whose ending changes with the case need a lookup instead of a backreference
SUBS += [
    (r"Корчм(а|и|і|у|ою) Щура", lambda m: {"а": "Щуряча корчма", "и": "Щурячої корчми", "і": "Щурячій корчмі",
                                          "у": "Щурячу корчму", "ою": "Щурячою корчмою"}[m.group(1)]),
    (r"Чудо-хлопчик(а|ові|ом|у)?\b", lambda m: {None: "Чудо-хлопець", "а": "Чудо-хлопця", "ові": "Чудо-хлопцеві",
                                                "ом": "Чудо-хлопцем", "у": "Чудо-хлопцю"}[m.group(1)]),
]

# rules applied only when the English line contains the given word (Woozle ≠ real «вузли» = knots)
ONLY_IF = [("oozle", r"\bВузл(и|ів|ам|ами|ах)\b", r"Візл\1"), ("oozle", r"\bВузл\b", "Візл"),
           ("oozle", r"\bВузлик(и|ів)\b", r"Візл\1")]
en = {}
for f in glob.glob(str(b / "[AB]*.jsonl")):
    for r in map(json.loads, open(f, encoding="utf-8")):
        en[r["id"]] = r["en"]
out = {}
for f in sorted(glob.glob(str(b / "out" / "*.jsonl"))):
    if f.endswith("zz_final.jsonl"):
        continue
    for line in open(f, encoding="utf-8"):
        if line.strip():
            o = json.loads(line)
            out[o["id"]] = o
hits = collections.Counter()
fixed = {}
for i, o in out.items():
    uk = o["uk"]
    rules = SUBS + [(a, r) for w, a, r in ONLY_IF if w in en.get(i, "")]
    for a, r in rules:
        new = re.sub(a, r, uk)
        if new != uk:
            hits[a] += 1
            uk = new
    if uk != o["uk"]:
        fixed[i] = {**o, "uk": uk}
with open(b / "out" / "zz_final.jsonl", "w", encoding="utf-8") as fh:
    for i in sorted(fixed):
        fh.write(json.dumps(fixed[i], ensure_ascii=False) + "\n")
print("lines changed:", len(fixed))
for a, n in hits.most_common():
    print(f"  {n:5d}  {a}")
