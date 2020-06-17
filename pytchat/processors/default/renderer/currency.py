'''
YouTubeスーパーチャットで使用される通貨の記号とレート検索用の略号の
対応表
Key：
    YouTubeスーパーチャットで使用される通貨の記号
    （アルファベットで終わる場合、0xA0(&npsp)が付く）
Value:
    fxtext: 3文字の通貨略称
    jptest: 日本語テキスト
'''
symbols = {
    "$": {"fxtext": "USD", "jptext": "米・ドル"},
    "A$": {"fxtext": "AUD", "jptext": "オーストラリア・ドル"},
    "CA$": {"fxtext": "CAD", "jptext": "カナダ・ドル"},
    "CHF\xa0": {"fxtext": "CHF", "jptext": "スイス・フラン"},
    "COP\xa0": {"fxtext": "COP", "jptext": "コロンビア・ペソ"},
    "HK$": {"fxtext": "HKD", "jptext": "香港・ドル"},
    "HUF\xa0": {"fxtext": "HUF", "jptext": "ハンガリー・フォリント"},
    "MX$": {"fxtext": "MXN", "jptext": "メキシコ・ペソ"},
    "NT$": {"fxtext": "TWD", "jptext": "台湾・ドル"},
    "NZ$": {"fxtext": "NZD", "jptext": "ニュージーランド・ドル"},
    "PHP\xa0": {"fxtext": "PHP", "jptext": "フィリピン・ペソ"},
    "PLN\xa0": {"fxtext": "PLN", "jptext": "ポーランド・ズロチ"},
    "R$": {"fxtext": "BRL", "jptext": "ブラジル・レアル"},
    "RUB\xa0": {"fxtext": "RUB", "jptext": "ロシア・ルーブル"},
    "SEK\xa0": {"fxtext": "SEK", "jptext": "スウェーデン・クローナ"},
    "£": {"fxtext": "GBP", "jptext": "英・ポンド"},
    "₩": {"fxtext": "KRW", "jptext": "韓国・ウォン"},
    "€": {"fxtext": "EUR", "jptext": "欧・ユーロ"},
    "₹": {"fxtext": "INR", "jptext": "インド・ルピー"},
    "￥": {"fxtext": "JPY", "jptext": "日本・円"},
    "PEN\xa0": {"fxtext": "PEN", "jptext": "ペルー・ヌエボ・ソル"},
    "ARS\xa0": {"fxtext": "ARS", "jptext": "アルゼンチン・ペソ"},
    "CLP\xa0": {"fxtext": "CLP", "jptext": "チリ・ペソ"},
    "NOK\xa0": {"fxtext": "NOK", "jptext": "ノルウェー・クローネ"},
    "BAM\xa0": {"fxtext": "BAM", "jptext": "ボスニア・兌換マルカ"},
    "SGD\xa0": {"fxtext": "SGD", "jptext": "シンガポール・ドル"}
}
