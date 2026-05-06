from flask import flash, url_for, redirect, render_template, request, Blueprint
from utils import login_required, get_supabase
import datetime

a_receber_bp = Blueprint("a_receber", __name__)


@a_receber_bp.route("/a-receber", methods=["GET", "POST"])
@a_receber_bp.route("/a-receber/<int:id>", methods=["GET", "POST"])
@login_required
def a_receber(id=None):
    sb = get_supabase()

    # DELETE
    delete_id = request.args.get("delete_id")
    if delete_id:
        sb.table("a_receber").delete().eq("id", delete_id).execute()
        flash("Registro excluído com sucesso!", "success")
        return redirect(url_for("a_receber.a_receber"))

    # POST
    if request.method == "POST":
        descricao    = request.form.get("descricao", "").strip()
        descricao    = descricao[0].upper() + descricao[1:] if descricao else descricao
        devedor      = request.form.get("devedor", "").strip()
        valor_total  = float(request.form.get("valor_total"))
        num_parcelas = int(request.form.get("num_parcelas", 1))
        observacao   = (request.form.get("observacao", "") or "").strip() or None

        if id:
            sb.table("a_receber").update({
                "descricao":    descricao,
                "devedor":      devedor,
                "valor_total":  valor_total,
                "num_parcelas": num_parcelas,
                "observacao":   observacao
            }).eq("id", id).execute()
            flash("Registro atualizado com sucesso!", "success")
        else:
            res = sb.table("a_receber").insert({
                "descricao":    descricao,
                "devedor":      devedor,
                "valor_total":  valor_total,
                "num_parcelas": num_parcelas,
                "observacao":   observacao
            }).execute()

            novo_id       = res.data[0]["id"]
            valor_parcela = round(valor_total / num_parcelas, 2)
            parcelas      = [
                {"a_receber_id": novo_id, "numero": i + 1, "valor": valor_parcela}
                for i in range(num_parcelas)
            ]
            sb.table("a_receber_parcela").insert(parcelas).execute()
            flash("Registro criado com sucesso!", "success")

        return redirect(url_for("a_receber.a_receber"))

    # GET
    registro = None
    if id:
        res = sb.table("a_receber").select("*").eq("id", id).execute()
        if res.data:
            registro = res.data[0]
        else:
            flash("Registro não encontrado!", "danger")
            return redirect(url_for("a_receber.a_receber"))

    registros = sb.table("a_receber").select("""
        *, parcelas: a_receber_parcela (*)
    """).order("id", desc=True).execute().data

    return render_template("a_receber.html", registros=registros, registro=registro)


@a_receber_bp.route("/a-receber/receber/<int:parcela_id>")
@login_required
def receber_parcela(parcela_id):
    sb = get_supabase()

    res = sb.table("a_receber_parcela").select("*, a_receber(descricao, devedor)").eq("id", parcela_id).execute()
    if not res.data:
        flash("Parcela não encontrada!", "danger")
        return redirect(url_for("a_receber.a_receber"))

    parcela = res.data[0]

    # Gera entrada automática
    transacao = sb.table("transacao").insert({
        "descricao": f"{parcela['a_receber']['descricao']} ({parcela['a_receber']['devedor']})",
        "valor":     parcela["valor"],
        "data":      datetime.date.today().isoformat(),
        "tipo":      "entrada",
    }).execute()

    transacao_id = transacao.data[0]["id"]

    # Marca parcela como recebida
    sb.table("a_receber_parcela").update({
        "recebido":     True,
        "transacao_id": transacao_id
    }).eq("id", parcela_id).execute()

    flash("Parcela recebida e entrada gerada automaticamente!", "success")
    return redirect(url_for("a_receber.a_receber"))