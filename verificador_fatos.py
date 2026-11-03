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
    "A cidade de São Paulo tem cerca de 11,4 milhões de habitantes.",
    "O Brasil tem 26 estados e um Distrito Federal.",
    "O rio Amazonas é o maior rio do mundo em volume de água.",
    "A Constituição brasileira atual foi promulgada em 1988.",
    "A Copa do Mundo de 2002 foi vencida pelo Brasil.",
    "O Brasil proclamou a independência em 1822.",
    "A língua oficial do Brasil é o português.",
]

# Conjunto de testes: (afirmação, veredito esperado)
TESTES = [
    ("Brasília é a capital do Brasil.", "apoiada"),
    ("A capital do Brasil é Brasília.", "apoiada"),
    ("O Brasil proclamou a independência em 1822.", "apoiada"),
    ("A cidade de São Paulo tem 12 milhões de habitantes.", "refutada"),
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


if __name__ == "__main__":
    main()
