"""
Verificador simples de fatos em português (sem dependências externas).

Fluxo:
1. Recupera o fato da base mais parecido com a afirmação (sobreposição de palavras).
2. Para afirmações com números, compara os valores (com arredondamento).
3. Para afirmações "X é Y", compara sujeito e predicado, não só as palavras.
4. Dá um veredito: apoiada, refutada ou sem evidência suficiente.

Uso:
    python3 verificador_fatos.py                         # roda o conjunto de testes
    python3 verificador_fatos.py "A capital do Brasil é Brasília."
    python3 verificador_fatos.py --interativo            # digite afirmações uma a uma
"""

import re
import sys
import unicodedata


def normalizar(texto):
    """Minúsculas e sem acentos: 'Brasília' -> 'brasilia'."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


STOPWORDS = {normalizar(w) for w in """
a o as os de da do das dos e em no na nos nas um uma uns umas que é foi são ser
tem têm por para com se ao aos à às mais seu sua seus suas pelo pela
""".split()}

PALAVRAS_UNICAS = {"capital", "presidente", "maior", "menor", "primeiro", "primeira",
                   "unico", "unica", "ultimo", "ultima"}

ESCALAS = {"mil": 1e3, "milhao": 1e6, "milhoes": 1e6, "bilhao": 1e9, "bilhoes": 1e9}


BASE_EVIDENCIAS = [
    "A capital do Brasil é Brasília.",
    "Brasília é a capital federal do Brasil desde 1960.",
    "Brasília foi inaugurada em 1960.",
    "O Rio de Janeiro foi a capital do Brasil até 1960.",
    "São Paulo é a maior cidade do Brasil.",
    "A capital do estado de São Paulo é a cidade de São Paulo.",
    "O Brasil tem 26 estados e um Distrito Federal.",
    "O rio Amazonas é o maior rio do mundo em volume de água.",
    "A Constituição brasileira foi promulgada em 1988.",
    "A Copa do Mundo de 2002 foi vencida pelo Brasil.",
    "O Brasil proclamou a independência em 1822.",
    "A língua oficial do Brasil é o português.",
    "O Brasil faz fronteira com 10 países.",
    "A capital da Argentina é Buenos Aires.",
    "O Brasil é o maior país da América do Sul em área.",
    "A capital da França é Paris.",
    "A capital do Japão é Tóquio.",
    "A capital de Portugal é Lisboa.",
    "A capital da Alemanha é Berlim.",
    "A capital do Canadá é Ottawa.",
    "A capital da Austrália é Canberra.",
    "O monte Everest é a montanha mais alta do mundo.",
    "O oceano Pacífico é o maior oceano do mundo.",
    "A Rússia é o maior país do mundo em área.",
    "O Egito fica no continente africano.",
    "A Antártida é o continente mais frio do planeta.",
    "A torre Eiffel fica em Paris.",
    "A água ferve a 100 graus Celsius ao nível do mar.",
    "A água congela a 0 graus Celsius ao nível do mar.",
    "A fórmula química da água é H2O.",
    "O símbolo químico do ouro é Au.",
    "A Terra gira em torno do Sol.",
    "A Lua é o único satélite natural da Terra.",
    "Júpiter é o maior planeta do Sistema Solar.",
    "A Terra é o terceiro planeta a partir do Sol.",
    "A velocidade da luz no vácuo é de cerca de 300 mil quilômetros por segundo.",
    "O número pi é aproximadamente 3,14.",
    "O corpo humano adulto tem 206 ossos.",
    "O ser humano tem 2 pulmões.",
    "Um ano comum tem 365 dias.",
    "Uma semana tem 7 dias.",
    "Um dia tem 24 horas.",
    "Uma hora tem 60 minutos.",
    "Um triângulo tem 3 lados.",
    "Um quadrado tem 4 lados.",
    "A soma dos ângulos internos de um triângulo é 180 graus.",
    "A Segunda Guerra Mundial terminou em 1945.",
    "O ser humano pisou na Lua pela primeira vez em 1969.",
    "A Revolução Francesa começou em 1789.",
    "Leonardo da Vinci pintou a Mona Lisa.",
    "William Shakespeare escreveu a peça Romeu e Julieta.",
    "O Brasil é uma república federativa.",
]


# Conjunto de testes: (afirmação, veredito esperado)
TESTES = [
    ("Brasília é a capital do Brasil.", "apoiada"),
    ("A capital do Brasil é Brasília.", "apoiada"),
    ("São Paulo é a capital do Brasil.", "refutada"),
    ("O Rio de Janeiro é a capital do Brasil.", "refutada"),
    ("O Brasil proclamou a independência em 1822.", "apoiada"),
    ("A Constituição brasileira foi promulgada em 1988.", "apoiada"),
    ("A Constituição brasileira foi promulgada em 1998.", "refutada"),
    ("A língua oficial do Brasil é o português.", "apoiada"),
    ("O Brasil tem 26 estados e um Distrito Federal.", "apoiada"),
    ("O Brasil tem 27 estados.", "refutada"),
    ("A água ferve a 100 graus Celsius ao nível do mar.", "apoiada"),
    ("A água ferve a 90 graus Celsius ao nível do mar.", "refutada"),
    ("A Alemanha é o país mais populoso da Europa.", "sem evidência suficiente"),
]


# ---------- Texto e palavras ----------

def palavras(texto):
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def tokens(texto):
    """Palavras relevantes (sem stopwords)."""
    return {p for p in palavras(texto) if p not in STOPWORDS}


def cobertura(a, b):
    """Fração das palavras de 'a' que aparecem em 'b'."""
    ta = tokens(a)
    if not ta:
        return 0.0
    return len(ta & tokens(b)) / len(ta)


def bigramas(texto):
    p = palavras(texto)
    return {f"{p[i]} {p[i + 1]}" for i in range(len(p) - 1)}


def fracao_bigramas(a, b):
    ba = bigramas(a)
    return len(ba & bigramas(b)) / len(ba) if ba else 0.0


def tem_palavra_unica(texto):
    return any(p in PALAVRAS_UNICAS for p in palavras(texto))


# ---------- Números com escala ----------

def extrair_numeros(texto):
    """Lista de valores: '12 milhões' -> 12 000 000; '12.396.372' -> 12 396 372."""
    t = re.sub(r"(\d)[\s  ](?=\d{3}(?!\d))", r"\1", texto)
    achados = []
    padrao = r"(\d+(?:[.,]\d+)*)(?:\s*(milh[õo]es|milh[ãa]o|bilh[õo]es|bilh[ãa]o|mil)\b)?"
    for m in re.finditer(padrao, t, re.I):
        s = m.group(1)
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
            s = s.replace(".", "")
        elif "," in s:
            s = s.replace(".", "").replace(",", ".")
        valor = float(s)
        grupo = m.group(2)
        escala = ESCALAS.get(normalizar(grupo)) if grupo else None
        casas = len(s.split(".")[1]) if "." in s else 0
        unidade = 1.0
        if escala:
            valor *= escala
            unidade = (10 ** -casas) * escala
        achados.append({"valor": valor, "escala": bool(escala), "unidade": unidade})
    return achados


def numero_bate(afirmado, encontrado):
    if not afirmado["escala"]:
        return afirmado["valor"] == encontrado["valor"]
    # "12 milhões" aceita valores que arredondam para 12 milhões (de 11,5 a 12,5)
    meio = afirmado["unidade"] / 2
    return encontrado["valor"] >= afirmado["valor"] - meio and encontrado["valor"] < afirmado["valor"] + meio


# ---------- Relações "X é Y" ----------

def partir(texto):
    """Separa sujeito e predicado no primeiro verbo de ligação."""
    t = re.sub(r"[.!?]+$", "", texto)
    m = re.search(r"\s+(?:é|são|foi|foram|era|eram)\s+", t, re.I)
    if not m:
        return None
    return t[:m.start()], t[m.end():]


def julgar_relacao(afirmacao, evidencia):
    c, e = partir(afirmacao), partir(evidencia)
    if not c or not e:
        return None
    cs, cp = c
    es, ep = e

    direto = cobertura(cs, es) >= 0.8 and cobertura(cp, ep) >= 0.8
    inverso = cobertura(cs, ep) >= 0.8 and cobertura(cp, es) >= 0.8
    if direto or inverso:
        # "foi ... até 1960" já encerrou: não sustenta uma afirmação no presente
        encerrado = re.search(r"\sat[ée]\s", " " + evidencia + " ", re.I) and re.search(r"\s(é|são)\s", afirmacao, re.I)
        if not encerrado:
            return "apoiada"
        return "refutada" if tem_palavra_unica(cp) else "sem evidência suficiente"

    sujeito_bate = cobertura(cs, es) >= 0.8 or cobertura(cs, ep) >= 0.8
    predicado_bate = cobertura(cp, ep) >= 0.8 or cobertura(cp, es) >= 0.8
    unico = tem_palavra_unica(cp) or tem_palavra_unica(ep)
    if unico and sujeito_bate != predicado_bate:
        return "refutada"
    return "sem evidência suficiente"


def julgar(afirmacao, evidencia, score):
    na = extrair_numeros(afirmacao)
    nf = extrair_numeros(evidencia)
    if na:
        if not nf:
            return "sem evidência suficiente"
        todos = all(any(numero_bate(v, n) for n in nf) for v in na)
        return "apoiada" if todos else "refutada"
    relacao = julgar_relacao(afirmacao, evidencia)
    if relacao:
        return relacao
    return "apoiada" if score >= 0.8 and fracao_bigramas(afirmacao, evidencia) >= 0.5 else "sem evidência suficiente"


# ---------- Recuperação e veredito ----------

def recuperar(afirmacao, base):
    melhor, melhor_score = None, 0.0
    for fato in base:
        score = cobertura(afirmacao, fato)
        if score > melhor_score:
            melhor, melhor_score = fato, score
    return melhor, melhor_score


def verificar(afirmacao, base, limiar=0.5):
    """Retorna (veredito, evidência usada, pontuação de similaridade)."""
    fato, score = recuperar(afirmacao, base)
    if fato is None or score < limiar:
        return "sem evidência suficiente", None, score
    return julgar(afirmacao, fato, score), fato, score


# ---------- Interface de linha de comando ----------

def main():
    if len(sys.argv) > 1 and sys.argv[1] != "--interativo":
        afirmacao = " ".join(sys.argv[1:])
        veredito, fato, score = verificar(afirmacao, BASE_EVIDENCIAS)
        print(f"Afirmação: {afirmacao}")
        print(f"Veredito:  {veredito}")
        if fato:
            print(f"Evidência ({score:.2f}): {fato}")
        return

    print(f"{'AFIRMAÇÃO':<56} {'VEREDITO':<26} {'ESPERADO':<26} OK")
    print("-" * 120)
    acertos = 0
    for afirmacao, esperado in TESTES:
        veredito, fato, score = verificar(afirmacao, BASE_EVIDENCIAS)
        ok = veredito == esperado
        acertos += ok
        print(f"{afirmacao:<56} {veredito:<26} {esperado:<26} {'sim' if ok else 'NÃO'}")
        if fato:
            print(f"    evidência ({score:.2f}): {fato}")
    print(f"\nAcurácia: {acertos}/{len(TESTES)} = {acertos / len(TESTES):.0%}")


def modo_interativo():
    print("Verificador de fatos. Digite uma afirmação (linha vazia encerra).\n")
    while True:
        try:
            afirmacao = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not afirmacao:
            break
        veredito, fato, score = verificar(afirmacao, BASE_EVIDENCIAS)
        print(f"  Veredito: {veredito.upper()}")
        if fato:
            print(f"  Evidência ({score:.2f}): {fato}")
        print()


if __name__ == "__main__":
    if sys.argv[1:] == ["--interativo"]:
        modo_interativo()
    else:
        main()
