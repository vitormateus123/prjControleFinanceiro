from flask import render_template, request, redirect, url_for, flash, Blueprint
from datetime import datetime
from utils import get_supabase, login_required

transacoes_bp = Blueprint("transacoes", __name__)

@transacoes_bp.route("/transacoes", methods=["GET", "POST"])
@transacoes_bp.route("/transacoes/<int:id>", methods=["GET", "POST"])
@login_required
def transacoes(id=None):
    sb = get_supabase()

    if request.method == "POST":
        descricao          = request.form.get("descricao", "").strip()
        valor_raw          = request.form.get("valor")
        data               = request.form.get("data")
        tipo               = request.form.get("tipo")
        categoria_id       = request.form.get("categoria_id")
        forma_pagamento_id = request.form.get("forma_pagamento_id")
        forma_origem_id    = request.form.get("forma_origem_id")
        forma_destino_id   = request.form.get("forma_destino_id")

        if not valor_raw or not data or not tipo:
            flash("Preencha todos os campos!", "danger")
            return redirect(url_for("transacoes.transacoes"))

        if descricao[0].isLower():
            descricao[0].Upper() + descricao[1:]

        if tipo == "transferencia" and (not forma_origem_id or not forma_destino_id):
            flash("Informe a origem e o destino da transferência!", "danger")
            return redirect(url_for("transacoes.transacoes"))

        if tipo != "transferencia" and not categoria_id:
            flash("Selecione uma categoria!", "danger")
            return redirect(url_for("transacoes.transacoes"))

        try:
            valor = float(valor_raw)
            datetime.strptime(data, "%Y-%m-%d")
            categoria_id       = int(categoria_id)       if categoria_id       else None
            forma_pagamento_id = int(forma_pagamento_id) if forma_pagamento_id else None
            forma_origem_id    = int(forma_origem_id)    if forma_origem_id    else None
            forma_destino_id   = int(forma_destino_id)   if forma_destino_id   else None
        except ValueError:
            flash("Dados inválidos!", "danger")
            return redirect(url_for("transacoes.transacoes"))

        if valor <= 0:
            flash("Valor deve ser maior que zero!", "danger")
            return redirect(url_for("transacoes.transacoes"))

        dados = {
            "descricao":          descricao,
            "valor":              valor,
            "data":               data,
            "tipo":               tipo,
            "categoria_id":       categoria_id       if tipo != "transferencia" else None,
            "forma_pagamento_id": forma_pagamento_id if tipo == "saida"         else None,
            "forma_origem_id":    forma_origem_id    if tipo in ("entrada", "transferencia") else None,
            "forma_destino_id":   forma_destino_id   if tipo == "transferencia" else None,
        }

        if id:
            sb.table("transacao").update(dados).eq("id", id).execute()
            flash("Transação atualizada com sucesso!", "success")
        else:
            sb.table("transacao").insert(dados).execute()
            flash("Transação cadastrada com sucesso!", "success")

        return redirect(url_for("transacoes.transacoes"))

    transacao = None
    if id:
        res = sb.table("transacao").select("*").eq("id", id).execute()
        if res.data:
            transacao = res.data[0]
        else:
            flash("Transação não encontrada!", "danger")
            return redirect(url_for("transacoes.transacoes"))

    delete_id = request.args.get("delete_transacao")
    if delete_id:
        sb.table("transacao").delete().eq("id", delete_id).execute()
        flash("Transação excluída com sucesso!", "success")
        return redirect(url_for("transacoes.transacoes"))

    transacoes_list = get_supabase().table("transacao").select("""
        *,
        categoria:       categoria_id       (nome),
        forma:           forma_pagamento_id (nome),
        origem:          forma_origem_id    (nome),
        destino:         forma_destino_id   (nome)
    """).order("id", desc=False).execute().data

    categorias = get_supabase().table("categoria").select("*").execute().data
    formas = get_supabase().table("forma_pagamento").select("*").execute().data

    return render_template(
        "transacao.html",
        transacoes=transacoes_list,
        categorias=categorias,
        formas=formas,
        transacao=transacao
    )