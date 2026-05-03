from flask import Flask, render_template, request, redirect, url_for, flash
from services.supabase_client import supabase

app = Flask(__name__)
app.secret_key = "1234"

@app.route("/")
def index():
    return render_template("index.html")

# --------- Categoria ---------- 
@app.route("/categorias", methods=["GET", "POST"])
@app.route("/categorias/<int:id>", methods=["GET", "POST"])
def categorias(id=None):

    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")

        if id:
            supabase.table("categoria").update({
                "nome": nome,
                "tipo": tipo
            }).eq("id", id).execute()

            flash("Categoria atualizada com sucesso!", "success")

        else:
            supabase.table("categoria").insert({
                "nome": nome,
                "tipo": tipo
            }).execute()

            flash("Categoria criada com sucesso!", "success")

        return redirect(url_for("categorias"))

    categoria = None

    if id:
        res = supabase.table("categoria").select("*").eq("id", id).execute()

        if res.data:
            categoria = res.data[0]
        else:
            flash("Categoria não encontrada!", "danger")
            return redirect(url_for("categorias"))
        
    delete_id = request.args.get("delete_categoria")

    if delete_id:
        supabase.table("categoria").delete().eq("id", delete_id).execute()
        flash("Categoria excluída com sucesso!", "success")
        return redirect(url_for("categorias"))

    categorias = supabase.table("categoria").select("*").order("id", desc=False).execute().data

    return render_template(
        "categoria.html",
        categorias=categorias,
        categoria=categoria
    )

# -------- Pagamentos ---------
@app.route("/pagamentos", methods=["GET", "POST"])
@app.route("/pagamentos/<int:id>", methods=["GET", "POST"])

def pagamentos(id=None):
    if request.method == "POST":
        nome = request.form.get("nome")
        
        if id:
            supabase.table("forma_pagamento").update({
                "nome": nome
            }).eq("id", id).execute()
            
            flash("Pagamento atualizado com sucesso!", "success")
        else:
            supabase.table("forma_pagamento").insert({
                "nome": nome
            }).execute()
            
            flash("Pagamento criado com sucesso!", "success")

        return redirect(url_for("pagamentos"))
    
    pagamento = None
    
    if id:   
        res = supabase.table("forma_pagamento").select("*").eq("id", id).execute()

        if res.data:
            pagamento = res.data[0]
        else:
            flash("Forma de pagamento não encontrada!", "danger")
            return redirect(url_for("pagamentos"))
        
    delete_id = request.args.get("delete_pagamento")

    if delete_id:
        supabase.table("forma_pagamento").delete().eq("id", delete_id).execute()
        flash("Forma de pagamento excluída com sucesso!", "success")
        return redirect(url_for("pagamentos"))

        
    formas = supabase.table("forma_pagamento").select("*").order("id", desc=False).execute().data
    
    return render_template(
        "pagamento.html",
        pagamentos=formas,
        pagamento=pagamento
    )
# --------- Transações ----------
@app.route("/transacoes", methods=["GET", "POST"])
@app.route("/transacoes/<int:id>", methods=["GET", "POST"])
def transacoes(id=None):

    if request.method == "POST":
        descricao = request.form.get("descricao")
        valor = float(request.form.get("valor"))
        data = request.form.get("data")
        tipo = request.form.get("tipo")
        categoria_id = int(request.form.get("categoria_id"))
        forma_pagamento_id = int(request.form.get("forma_pagamento_id"))

        if id:
            supabase.table("transacao").update({
                "descricao": descricao,
                "valor": valor,
                "data": data,
                "tipo": tipo,
                "categoria_id": categoria_id,
                "forma_pagamento_id": forma_pagamento_id
            }).eq("id", id).execute()

            flash("Transação atualizada com sucesso!", "success")
        else:
            supabase.table("transacao").insert({
                "descricao": descricao,
                "valor": valor,
                "data": data,
                "tipo": tipo,
                "categoria_id": categoria_id,
                "forma_pagamento_id": forma_pagamento_id
            }).execute()

            flash("Transação cadastrada com sucesso!", "success")

        return redirect(url_for("transacoes"))

    # ---------------- GET ----------------
    transacao = None

    if id:
        res = supabase.table("transacao").select("*").eq("id", id).execute()

        if res.data:
            transacao = res.data[0]
        else:
            flash("Transação não encontrada!", "danger")
            return redirect(url_for("transacoes"))
        
        
    delete_id = request.args.get("delete_transacao")
    
    if delete_id:
        supabase.table("transacao").delete().eq("id", delete_id).execute()
        flash("Transação excluída com sucesso!", "success")
        return redirect(url_for("transacoes"))

    transacoes_list = supabase.table("transacao").select("""
        *,
        categoria: categoria_id (nome),
        forma: forma_pagamento_id (nome)
    """).order("id", desc=False).execute().data

    categorias = supabase.table("categoria").select("*").execute().data
    formas = supabase.table("forma_pagamento").select("*").execute().data

    return render_template(
        "transacao.html",
        transacoes=transacoes_list,
        categorias=categorias,
        formas=formas,
        transacao=transacao
    )
    
if __name__ == "__main__":
    app.run(debug=True)