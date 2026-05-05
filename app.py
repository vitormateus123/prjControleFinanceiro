from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
from config import SENHA
import os
from routes.transacoes import transacoes_bp
from utils import get_supabase, login_required

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(transacoes_bp)

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logado"):
        return redirect(url_for("index"))
    if request.method == "POST":
        if request.form.get("senha") == SENHA:
            session["logado"] = True
            return redirect(url_for("index"))
        flash("Senha incorreta!", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- INDEX ----------------
@app.route("/")
@login_required
def index():
    sb = get_supabase()
    transacoes = sb.table("transacao").select("""
        *, categoria: categoria_id (nome), forma: forma_pagamento_id (nome)
    """).order("data", desc=True).execute().data

    total_entradas = sum(t["valor"] for t in transacoes if t["tipo"] == "entrada")
    total_saidas   = sum(t["valor"] for t in transacoes if t["tipo"] == "saida")
    saldo          = total_entradas - total_saidas

    ultimas = transacoes[:5]

    porc_entradas = round((total_entradas / (total_entradas + total_saidas) * 100)) if (total_entradas + total_saidas) > 0 else 0
    porc_saidas   = 100 - porc_entradas

    return render_template("index.html",
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo=saldo,
        ultimas=ultimas,
        porc_entradas=porc_entradas,
        porc_saidas=porc_saidas,
        total_transacoes=len(transacoes)
    )

# --------- CATEGORIAS ----------
@app.route("/categorias", methods=["GET", "POST"])
@app.route("/categorias/<int:id>", methods=["GET", "POST"])
@login_required
def categorias(id=None):
    sb = get_supabase()

    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")

        nome = nome[0].upper() + nome[1:] if nome else nome


        if id:
            sb.table("categoria").update({"nome": nome, "tipo": tipo}).eq("id", id).execute()
            flash("Categoria atualizada com sucesso!", "success")
        else:
            sb.table("categoria").insert({"nome": nome, "tipo": tipo}).execute()
            flash("Categoria criada com sucesso!", "success")

        return redirect(url_for("categorias"))

    categoria = None
    if id:
        res = sb.table("categoria").select("*").eq("id", id).execute()
        if res.data:
            categoria = res.data[0]
        else:
            flash("Categoria não encontrada!", "danger")
            return redirect(url_for("categorias"))

    delete_id = request.args.get("delete_categoria")
    if delete_id:
        check = sb.table("transacao").select("id").eq("categoria_id", delete_id).limit(1).execute()
        if check.data:
            flash("Não é possível excluir: categoria em uso.", "danger")
            return redirect(url_for("categorias"))
        sb.table("categoria").delete().eq("id", delete_id).execute()
        flash("Categoria excluída com sucesso!", "success")
        return redirect(url_for("categorias"))

    categorias = sb.table("categoria").select("*").order("id", desc=False).execute().data
    return render_template("categoria.html", categorias=categorias, categoria=categoria)

# -------- PAGAMENTOS ----------
@app.route("/pagamentos", methods=["GET", "POST"])
@app.route("/pagamentos/<int:id>", methods=["GET", "POST"])
@login_required
def pagamentos(id=None):
    sb = get_supabase()

    if request.method == "POST":
        nome = request.form.get("nome")

        nome = nome[0].upper() + nome[1:] if nome else nome


        if id:
            sb.table("forma_pagamento").update({"nome": nome}).eq("id", id).execute()
            flash("Pagamento atualizado com sucesso!", "success")
        else:
            sb.table("forma_pagamento").insert({"nome": nome}).execute()
            flash("Pagamento criado com sucesso!", "success")
        return redirect(url_for("pagamentos"))

    pagamento = None
    if id:
        res = sb.table("forma_pagamento").select("*").eq("id", id).execute()
        if res.data:
            pagamento = res.data[0]
        else:
            flash("Forma de pagamento não encontrada!", "danger")
            return redirect(url_for("pagamentos"))

    delete_id = request.args.get("delete_pagamento")
    if delete_id:
        check = sb.table("transacao").select("id").eq("forma_pagamento_id", delete_id).limit(1).execute()
        if check.data:
            flash("Não é possível excluir: forma de pagamento em uso.", "danger")
            return redirect(url_for("pagamentos"))
        sb.table("forma_pagamento").delete().eq("id", delete_id).execute()
        flash("Forma de pagamento excluída com sucesso!", "success")
        return redirect(url_for("pagamentos"))

    formas = sb.table("forma_pagamento").select("*").order("id", desc=False).execute().data
    return render_template("pagamento.html", pagamentos=formas, pagamento=pagamento)



@app.template_filter('data_br')
def data_br(value):
    return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
