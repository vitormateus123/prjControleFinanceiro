from flask import Flask, render_template, request, redirect, url_for, flash
from services.supabase_client import supabase

app = Flask(__name__)
app.secret_key = "1234"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/categorias", methods=["GET", "POST"])
def categorias():
    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")

        supabase.table("categoria").insert({
            "nome": nome,
            "tipo": tipo
        }).execute()
        
        flash("Categoria criada com sucesso!", "success")
        
        return redirect(url_for("categorias"))

    res = supabase.table("categoria").select("*").execute()
    categorias = res.data

    return render_template("categoria.html", categorias=categorias)

@app.route("/pagamentos", methods=["GET", "POST"])
def pagamentos():
    if request.method == "POST":
        nome = request.form.get("nome")
        
        supabase.table("forma_pagamento").insert({
            "nome": nome
        }).execute()
        
        flash("Pagamento criado com sucesso!", "success")

        
        return redirect(url_for("pagamentos"))
        
    res = supabase.table("forma_pagamento").select("*").execute()
    pagamentos = res.data
    
    return render_template("pagamento.html", pagamentos=pagamentos)

@app.route("/transacoes", methods=["GET", "POST"])
def transacoes():
    if request.method == "POST":
        descricao = request.form.get("descricao")
        valor = float(request.form.get("valor"))
        data = request.form.get("data")
        tipo = request.form.get("tipo")
        categoria_id = int(request.form.get("categoria_id"))
        forma_pagamento_id = int(request.form.get("forma_pagamento_id"))

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

    transacoes = supabase.table("transacao").select("*").execute().data
    categorias = supabase.table("categoria").select("*").execute().data
    formas = supabase.table("forma_pagamento").select("*").execute().data

    return render_template(
        "transacao.html",
        transacoes=transacoes,
        categorias=categorias,
        formas=formas
    )
    
if __name__ == "__main__":
    app.run(debug=True)