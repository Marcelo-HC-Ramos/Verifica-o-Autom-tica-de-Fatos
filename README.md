# Verificador simples de fatos em português

Aplicação prática de Processamento de Linguagem Natural (PLN) que verifica
automaticamente afirmações factuais contra uma base de evidências.

## Como funciona

1. **Base de evidências:** 52 fatos verificáveis (capitais, geografia, ciência, datas).
2. **Recuperação:** encontra o fato mais parecido com a afirmação, por sobreposição de palavras
   (sem acentos e sem stopwords).
3. **Veredito:**
   - `apoiada`: os números da afirmação aparecem no fato encontrado.
   - `refutada`: a afirmação traz um número diferente do fato.
   - `sem evidência suficiente`: nenhum fato é parecido o bastante.

## Requisitos

- Python 3.8 ou superior. Nenhuma biblioteca externa.

## Uso

```bash
python3 verificador_fatos.py                                  # roda os testes
python3 verificador_fatos.py "O Brasil tem 27 estados."       # verifica uma afirmação
```

## Limitações

- Negações e trocas de palavra não são entendidas ("Rio de Janeiro" contra "Brasília"
  retorna "sem evidência suficiente", não "refutada").
- Escalas não são convertidas ("12 milhões" e "12 mil" são tratados como números diferentes).
- A base local tem 52 fatos gerais; fatos fora dela não são verificados pelo terminal.

## Próximos passos

- Usar TF-IDF (`scikit-learn`) na recuperação.
- Trocar a base por um CSV ou JSON maior, com fontes confiáveis.
- Adicionar um modelo de inferência de linguagem natural (NLI) para lidar com negações.
