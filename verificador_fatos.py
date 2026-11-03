"""
Verificador simples de fatos em português (sem dependências externas).

Fluxo:
1. Recupera o fato da base mais parecido com a afirmação (sobreposição de palavras).
2. Compara os números da afirmação com os números do fato encontrado.
3. Dá um veredito: apoiada, refutada ou sem evidência suficiente.

Uso:
    python3 verificador_fatos.py                         # roda o conjunto de testes
    python3 verificador_fatos.py "A capital do Brasil é Brasília."
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


# Base de evidências: fatos conhecidos e verificáveis
BASE_EVIDENCIAS = [
    "A capital do Brasil é Brasília.",
    "O Brasil tem 26 estados e um Distrito Federal.",
    "O rio Amazonas é o maior rio do mundo em volume de água.",
    "A Constituição brasileira atual foi promulgada em 1988.",
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
    ("O Brasil proclamou a independência em 1822.", "apoiada"),
    ("A água ferve a 90 graus Celsius ao nível do mar.", "refutada"),
    ("A Constituição brasileira atual foi promulgada em 1988.", "apoiada"),
    ("A Constituição brasileira atual foi promulgada em 1998.", "refutada"),
    ("A língua oficial do Brasil é o português.", "apoiada"),
    ("O Brasil tem 26 estados e um Distrito Federal.", "apoiada"),
    ("O Brasil tem 27 estados.", "refutada"),
    ("O Brasil conquistou a Copa do Mundo de 2002.", "apoiada"),
    ("A Alemanha é o país mais populoso da Europa.", "sem evidência suficiente"),
]


def tokens(texto):
    """Conjunto de palavras relevantes (sem acento, sem stopwords)."""
    palavras = re.findall(r"[a-z0-9]+", normalizar(texto))
    return {p for p in palavras if p not in STOPWORDS}


def numeros(texto):
    """Números do texto. Remove separador de milhar ('2.000' -> '2000')."""
    return set(re.findall(r"\d+", texto.replace(".", "")))


def recuperar(afirmacao, base):
    """Devolve o fato da base mais parecido e a fração de palavras da afirmação que ele cobre."""
    ta = tokens(afirmacao)
    if not ta:
        return None, 0.0
    melhor, melhor_score = None, 0.0
    for fato in base:
        score = len(ta & tokens(fato)) / len(ta)
        if score > melhor_score:
            melhor, melhor_score = fato, score
    return melhor, melhor_score


def verificar(afirmacao, base, limiar=0.5):
    """Retorna (veredito, evidência usada, pontuação de similaridade)."""
    fato, score = recuperar(afirmacao, base)
    if fato is None or score < limiar:
        return "sem evidência suficiente", None, score

    na, nf = numeros(afirmacao), numeros(fato)
    if na:
        # Todos os números da afirmação precisam aparecer no fato
        veredito = "apoiada" if na <= nf else "refutada"
    else:
        # Sem números: só aceita se quase todas as palavras batem
        veredito = "apoiada" if score >= 0.8 else "sem evidência suficiente"
    return veredito, fato, score


def main():
    if len(sys.argv) > 1:
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
        marca = "sim" if ok else "NÃO"
        print(f"{afirmacao:<56} {veredito:<26} {esperado:<26} {marca}")
        if fato:
            print(f"    evidência ({score:.2f}): {fato}")

    total = len(TESTES)
    print(f"\nAcurácia: {acertos}/{total} = {acertos / total:.0%}")


def modo_interativo():
    """Digite afirmações uma a uma. Linha vazia encerra."""
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
