"""Стартовый набор карточек: обычный быт."""

FLASHCARD_SEED = [
    {
        "ru_text": "квартира",
        "en_variants": ["apartment", "flat"],
        "nuances": (
            "apartment — обычное слово в US для квартиры в многоквартирном доме.\n"
            "flat — то же значение в UK.\n"
            "Не flat в смысле «плоский» (a flat surface) — в бытовом контексте жилья это квартира.\n"
            "Не condominium / condo — это собственность с особым статусом, не синоним любой квартиры."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "уборка",
        "en_variants": ["cleaning", "housework"],
        "nuances": (
            "cleaning — процесс уборки: пыль, пол, поверхности.\n"
            "housework — домашние дела в целом: уборка, стирка, готовка и т.п.\n"
            "Если имеешь в виду только мытьё посуды — это другая карточка «помыть посуду» (do the dishes).\n"
            "Если имеешь в виду стирку — это другая карточка «постирать одежду» (do the laundry).\n"
            "Не clean-up как существительное в быту так часто не говорят; чаще cleaning / do the cleaning."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "холодильник",
        "en_variants": ["fridge", "refrigerator"],
        "nuances": (
            "fridge — разговорное короткое слово, самое естественное в речи.\n"
            "refrigerator — полное официальное название.\n"
            "Не freezer — это морозилка (отдельный отсек или отдельный прибор).\n"
            "fridge-freezer — холодильник с морозилкой в одном корпусе."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "стиральная машина",
        "en_variants": ["washing machine"],
        "nuances": (
            "washing machine — стиральная машина.\n"
            "Не dryer / tumble dryer — это сушилка для белья.\n"
            "Не dishwasher — это посудомоечная машина.\n"
            "Washer в US иногда говорят вместо washing machine, но washing machine понятнее.\n"
            "Связанная карточка «постирать одежду» — про действие (do the laundry), не про прибор."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "выключить свет",
        "en_variants": ["turn off the light", "switch off the light"],
        "nuances": (
            "turn off the light — самый частый вариант (US и общий).\n"
            "switch off the light — то же, чаще в UK.\n"
            "turn out the light — тоже ок, особенно в UK.\n"
            "Не shut down — это про компьютер или систему, не про лампочку.\n"
            "turn on / switch on — включить (противоположное)."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "заварить чай",
        "en_variants": ["make tea", "brew tea"],
        "nuances": (
            "make tea — самое естественное «заварить / сделать чай».\n"
            "brew tea — акцент именно на заваривании (время, крепость).\n"
            "Не cook tea — cook не используют для чая.\n"
            "make a cup of tea — одна чашка.\n"
            "put the kettle on — поставить чайник (шаг до заваривания)."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "помыть посуду",
        "en_variants": ["do the dishes", "wash the dishes"],
        "nuances": (
            "do the dishes — идиоматично и очень естественно.\n"
            "wash the dishes — тоже правильно и понятно.\n"
            "Не clean the dishes — чаще звучит как «очистить» в другом смысле, не как бытовая посудомойка руками.\n"
            "Не путать с карточкой «постирать одежду» — do the laundry про бельё, не про тарелки.\n"
            "Не путать с карточкой «уборка» — cleaning / housework шире, чем только посуда.\n"
            "dishwasher — посудомоечная машина; do the dishes может быть и руками, и с ней."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "сходить в магазин",
        "en_variants": ["go to the store", "go to the shop"],
        "nuances": (
            "go to the store — конкретный поход в магазин (US).\n"
            "go to the shop — то же в UK.\n"
            "go shopping — другое: «по магазинам» / шопинг без обязательной одной цели; не ставь как равный перевод этой карточки.\n"
            "run to the store — быстро сбегать за чем-то.\n"
            "Не go to the market без нужды — market чаще рынок, не любой супермаркет."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "очередь",
        "en_variants": ["queue", "line"],
        "nuances": (
            "queue — очередь (UK).\n"
            "line — очередь (US).\n"
            "stand in line / wait in line — стоять в очереди (US).\n"
            "wait in a queue / join the queue — стоять / встать в очередь (UK).\n"
            "Не queue как глагол «поставить в очередь» в IT — другое значение.\n"
            "Не row — это ряд, не очередь людей."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "сдача",
        "en_variants": ["change"],
        "nuances": (
            "change — сдача после оплаты купюрой.\n"
            "change также значит «мелочь» (loose change).\n"
            "Не exchange — обмен валюты или товара (exchange money / exchange a gift).\n"
            "Не refund — возврат денег за товар.\n"
            "Can I have the change? — можно сдачу?"
        ),
        "card_type": "word",
    },
    {
        "ru_text": "чек",
        "en_variants": ["receipt"],
        "nuances": (
            "receipt — кассовый чек / квитанция об оплате.\n"
            "check (US) — счёт в ресторане или кафе, не кассовый чек из магазина.\n"
            "bill — счёт в ресторане (UK) или счёт за услуги / банковский bill.\n"
            "Не check в смысле «проверить» (to check) — другое слово.\n"
            "Keep the receipt — сохраните чек."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "мне нужен пакет",
        "en_variants": ["I need a bag"],
        "nuances": (
            "bag — пакет или сумка в магазине.\n"
            "plastic bag / paper bag — уточнение материала.\n"
            "carrier bag — пакет для покупок (UK).\n"
            "Не packet — чаще маленькая упаковка еды (a packet of crisps), не пакет на кассе.\n"
            "Не pack — упаковывать / пачка, не «пакет»."
        ),
        "card_type": "sentence",
    },
    {
        "ru_text": "на работу",
        "en_variants": ["to work"],
        "nuances": (
            "to work — направление «на работу» (go to work).\n"
            "Без the: go to work, не go to the work.\n"
            "at work — «на работе» (уже там).\n"
            "in the office — в офисе как в конкретном месте.\n"
            "Не to the work — грамматически неверно в этом значении."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "опоздать",
        "en_variants": ["be late", "run late"],
        "nuances": (
            "be late — опоздать / быть поздно (I'm late).\n"
            "be late for something — опоздать на что-то (late for work / late for a meeting).\n"
            "run late — идти с опозданием по графику (I'm running late).\n"
            "Не late oneself — так не говорят.\n"
            "delay — задержка события или транспорта (the train was delayed).\n"
            "Не путать с карточкой «Я проспал» — overslept это причина опоздания, не само «опоздать»."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "Я проспал.",
        "en_variants": ["I overslept."],
        "nuances": (
            "I overslept — я проспал (нечаянно).\n"
            "sleep in — намеренно поспать подольше.\n"
            "Не I slept through без контекста — sleep through обычно «проспал событие / будильник».\n"
            "Не путать с карточкой «опоздать» — be late это результат; overslept может быть причиной.\n"
            "I overslept and was late for work — типичная связка двух идей."
        ),
        "card_type": "sentence",
    },
    {
        "ru_text": "зарядка для телефона",
        "en_variants": ["phone charger"],
        "nuances": (
            "phone charger — зарядка / зарядное устройство для телефона.\n"
            "charger — адаптер или устройство зарядки в целом.\n"
            "charging cable — только кабель.\n"
            "battery — батарея / аккумулятор внутри телефона, не зарядка.\n"
            "Не путать с карточкой «розетка» — socket / outlet это отверстие в стене, куда вставляют вилку."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "розетка",
        "en_variants": ["socket", "outlet"],
        "nuances": (
            "socket — розетка (UK).\n"
            "outlet / power outlet — розетка (US).\n"
            "plug — вилка на проводе, не розетка.\n"
            "Не путать с карточкой «зарядка для телефона» — charger это устройство зарядки.\n"
            "wall socket / wall outlet — розетка в стене."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "утюг",
        "en_variants": ["iron"],
        "nuances": (
            "iron — утюг (существительное).\n"
            "to iron — гладить утюгом.\n"
            "ironing board — гладильная доска.\n"
            "Не iron как «железо» (металл) без контекста быта — другое значение того же слова.\n"
            "steam iron — паровой утюг."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "постирать одежду",
        "en_variants": ["do the laundry", "wash the clothes"],
        "nuances": (
            "do the laundry — идиома: постирать / заняться стиркой.\n"
            "wash the clothes — тоже ок, чуть более буквально.\n"
            "laundry — и бельё для стирки, и сам процесс стирки.\n"
            "Не wash the laundry — обычно так не говорят; говорят do the laundry.\n"
            "Не путать с карточкой «помыть посуду» — do the dishes про посуду.\n"
            "Не путать с карточкой «стиральная машина» — washing machine это прибор, не действие.\n"
            "Не путать с карточкой «уборка» — cleaning / housework шире стирки."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "вынести мусор",
        "en_variants": ["take out the trash", "take out the rubbish"],
        "nuances": (
            "take out the trash — вынести мусор (US; garbage тоже US).\n"
            "take out the rubbish — то же (UK).\n"
            "take out — именно вынести (из дома к контейнеру).\n"
            "throw away / throw out — выбросить конкретный предмет в мусор.\n"
            "Не dump без контекста — грубее / про свалку.\n"
            "trash can / garbage can (US), bin (UK) — мусорное ведро."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "мне холодно",
        "en_variants": ["I'm cold", "I feel cold"],
        "nuances": (
            "I'm cold — мне холодно (ощущение тела).\n"
            "I feel cold — то же, чуть мягче по тону.\n"
            "It's cold — холодно вокруг (погода / комната), не про тебя.\n"
            "Не I have cold — так не говорят.\n"
            "I have a cold — «у меня простуда»; это другая карточка «простуда»."
        ),
        "card_type": "sentence",
    },
    {
        "ru_text": "простуда",
        "en_variants": ["a cold"],
        "nuances": (
            "a cold — простуда (have a cold / catch a cold).\n"
            "flu / the flu — грипп, обычно тяжелее простуды.\n"
            "cold / cool как температура — другое значение слова cold.\n"
            "Не путать с карточкой «мне холодно» — I'm cold это ощущение холода, не болезнь.\n"
            "Не I am a cold — так не говорят про болезнь."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "запись к врачу",
        "en_variants": ["a doctor's appointment"],
        "nuances": (
            "a doctor's appointment — запись / приём у врача на назначенное время.\n"
            "make an appointment / book an appointment — записаться.\n"
            "visit — визит в целом; appointment — именно заранее назначенный слот.\n"
            "Не date — свидание или календарная дата, не приём у врача.\n"
            "GP appointment — запись к терапевту (UK)."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "Можно открыть окно?",
        "en_variants": [
            "Can I open the window?",
            "Do you mind if I open the window?",
        ],
        "nuances": (
            "Can I open the window? — нейтральная вежливая просьба.\n"
            "Do you mind if I open the window? — вежливее: «вы не против…».\n"
            "May I open the window? — формальнее.\n"
            "Would you mind if I opened the window? — ещё вежливее (условная форма).\n"
            "Ответ на Do you mind…: No, I don't mind = можно открыть."
        ),
        "card_type": "sentence",
    },
    {
        "ru_text": "сесть на автобус",
        "en_variants": ["take the bus", "catch the bus"],
        "nuances": (
            "take the bus — воспользоваться автобусом / поехать на автобусе.\n"
            "catch the bus — успеть на автобус / сесть на него.\n"
            "get on the bus — действие посадки (войти в автобус).\n"
            "get off the bus — выйти из автобуса.\n"
            "Не sit on the bus как основной перевод «сесть на автобус» в смысле поездки — это скорее «сидеть в автобусе»."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "пробка",
        "en_variants": ["traffic jam", "stuck in traffic"],
        "nuances": (
            "traffic jam — затор, пробка на дороге.\n"
            "stuck in traffic — застрял в пробке / в плотном движении.\n"
            "heavy traffic — плотное движение; это не обязательно полный затор, поэтому не равный перевод «пробки».\n"
            "congestion — более формально: заторы / перегруженность дорог.\n"
            "cork — пробка от бутылки, не дорожная пробка."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "Я забыл ключи дома.",
        "en_variants": ["I left my keys at home.", "I forgot my keys."],
        "nuances": (
            "I left my keys at home — самое естественное: оставил / «забыл» ключи дома.\n"
            "I forgot my keys — тоже ок, но без места; с местом чаще left … at home.\n"
            "leave something somewhere — оставить что-то где-то.\n"
            "forget something — забыть взять / не вспомнить.\n"
            "Не I forgot my keys at home — носители чаще скажут left at home."
        ),
        "card_type": "sentence",
    },
    {
        "ru_text": "почистить зубы",
        "en_variants": ["brush your teeth"],
        "nuances": (
            "brush your teeth — стандартный перевод.\n"
            "clean your teeth — тоже встречается, особенно в UK.\n"
            "Не wash your teeth — так обычно не говорят.\n"
            "brush my teeth / I need to brush my teeth — смена лица и контекста.\n"
            "toothbrush — зубная щётка; toothpaste — зубная паста."
        ),
        "card_type": "phrase",
    },
    {
        "ru_text": "будильник",
        "en_variants": ["alarm", "alarm clock"],
        "nuances": (
            "alarm — будильник (часто на телефоне): set an alarm.\n"
            "alarm clock — физические часы-будильник.\n"
            "wake-up call — побудка в отеле (звонок на номер).\n"
            "Не alert в быту как замена alarm clock — другое слово.\n"
            "The alarm went off — будильник сработал."
        ),
        "card_type": "word",
    },
    {
        "ru_text": "На ужин будет суп.",
        "en_variants": ["We'll have soup for dinner.", "Dinner will be soup."],
        "nuances": (
            "We'll have soup for dinner — естественная формулировка.\n"
            "Dinner will be soup — короче, тоже понятно.\n"
            "have something for dinner — «на ужин будет / едим …».\n"
            "dinner — основной вечерний приём пищи; supper — разговорно / регионально.\n"
            "lunch — обед днём, не ужин."
        ),
        "card_type": "sentence",
    },
]
