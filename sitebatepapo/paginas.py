# Importações
from flask import render_template, redirect, url_for, request, flash, abort
from sitebatepapo import app, database, bcrypt
from sitebatepapo.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from sitebatepapo.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


# Páginas
@app.route('/')
def home():
    return render_template('home.html')


def guardar_id_post(post):
    id_post=post.id


@app.route('/batepapo')
@login_required
def batepapo():
    lista_posts = Post.query.all()
    return render_template('batepapo.html', lista_posts=lista_posts, guardar_id_post=guardar_id_post)


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()

        if usuario:

            if bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
                login_user(usuario, remember=form_login.lembrar_dados.data)
                flash(f'Login de {form_login.email.data} feito com sucesso!', 'alert-success')
                param_next = request.args.get('next')
                if param_next:
                    return redirect(param_next)
                else:
                    return redirect(url_for('home'))
            else:
                flash('Senha incorreta.', 'alert-danger')
        else:
            flash(f'Não existe um usuário cadastrado no email {form_login.email.data}', 'alert-danger')

    elif form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data)
        novo_usuario = Usuario(nome=form_criarconta.nome.data, email=form_criarconta.email.data, senha=senha_crypt)
        database.session.add(novo_usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso para {form_login.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Conta desconectada', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    texto_botao_editarperfil = 'Editar Perfil'
    funcao_pagina = 'editar_perfil'
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil, texto_botao_editarperfil=texto_botao_editarperfil, funcao_pagina=funcao_pagina)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form_criarpost = FormCriarPost()
    if form_criarpost.validate_on_submit():
        post = Post(corpo=form_criarpost.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com sucesso', 'alert-success')
        return redirect('http://127.0.0.1:5000/batepapo#footer')
    return render_template('criarpost.html', form_criarpost=form_criarpost)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def editar_post(post_id):
    print(post_id)
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
    else:
        form = None
    if request.method == 'GET':
        form.corpo.data = post.corpo
    elif form.validate_on_submit():
        post.corpo = form.corpo.data
        database.session.commit()
        return redirect('http://127.0.0.1:5000/batepapo#footer')
    return render_template('editarpost.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    print(post_id)
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        return redirect('http://127.0.0.1:5000/batepapo#footer')
    else:
        abort(403)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (600, 600)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_rpgs(form):
    lista_rpgs = []
    for campo in form:
        if 'rpg_' in campo.name:
            if campo.data == True:
                lista_rpgs.append(campo.label.text)
    return ';'.join(lista_rpgs)


def verificar_rpgs(form):
    lista_rpgs = current_user.rpgs.split(';')
    for campo in form:
        if 'rpg_' in campo.name:
            if campo.label.text in lista_rpgs:
                campo.data = True


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    texto_botao_editarperfil = 'Cancelar Edição'
    funcao_pagina = 'perfil'
    form_editar_perfil = FormEditarPerfil()
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    if form_editar_perfil.validate_on_submit():
        current_user.email = form_editar_perfil.email.data
        current_user.nome = form_editar_perfil.nome.data

        if form_editar_perfil.remover_foto.data == True:
            current_user.foto_perfil = 'default.jpg'
        elif form_editar_perfil.foto_perfil.data:
            current_user.foto_perfil = salvar_imagem(form_editar_perfil.foto_perfil.data)

        current_user.rpgs = atualizar_rpgs(form_editar_perfil)
        database.session.commit()
        flash('Perfil atualizado com sucesso.', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form_editar_perfil.email.data = current_user.email
        form_editar_perfil.nome.data = current_user.nome
        verificar_rpgs(form_editar_perfil)

    return render_template('editarperfil.html', foto_perfil=foto_perfil, form_editar_perfil=form_editar_perfil, texto_botao_editarperfil=texto_botao_editarperfil, funcao_pagina=funcao_pagina)