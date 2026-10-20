from flask import abort, request


def get_json_body():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        abort(400, description="O corpo da requisição deve ser um objeto JSON")
    return dados


def clean_text(valor, campo, max_len, required=True):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if required:
            abort(400, description=f"O campo '{campo}' é obrigatório")
        return None
    if not isinstance(valor, str):
        abort(400, description=f"O campo '{campo}' deve ser texto")
    valor = valor.strip()
    if len(valor) > max_len:
        abort(400, description=f"O campo '{campo}' deve ter no máximo {max_len} caracteres")
    return valor


def parse_int(valor, campo, minimo=None, maximo=None, required=True):
    if valor is None or valor == "":
        if required:
            abort(400, description=f"O campo '{campo}' é obrigatório")
        return None
    if isinstance(valor, (bool, float)):
        abort(400, description=f"O campo '{campo}' deve ser um número inteiro")
    try:
        n = int(valor)
    except (TypeError, ValueError):
        abort(400, description=f"O campo '{campo}' deve ser um número inteiro")
    if (minimo is not None and n < minimo) or (maximo is not None and n > maximo):
        abort(400, description=f"O campo '{campo}' deve estar entre {minimo} e {maximo}")
    return n


def paginacao_args(padrao=20, maximo=100):
    page = request.args.get("page", 1, type=int) or 1
    per_page = request.args.get("per_page", padrao, type=int) or padrao
    return max(page, 1), min(max(per_page, 1), maximo)