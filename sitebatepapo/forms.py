# Importações
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sitebatepapo.models import Usuario
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed

# Classes
class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de login')
    botao_submit_login = SubmitField('Fazer Login')


class FormCriarConta(FlaskForm):
    nome = StringField('Nome do Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da senha', validators=[DataRequired(), EqualTo('senha'), Length(6, 20)])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        cadastrado = Usuario.query.filter_by(email=email.data).first()
        if cadastrado:
            raise ValidationError('E-mail já cadastrado. Faça login ou crie uma conta com outro e-mail. ')


class FormEditarPerfil(FlaskForm):
    nome = StringField('Novo nome', validators=[DataRequired()])
    email = StringField('Novo e-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar foto de perfil.', validators=[FileAllowed(['jpg', 'png'])])
    remover_foto = BooleanField('Remover Foto')
    botao_submit_editar_perfil = SubmitField('Confirmar Edição')
    rpg_ceu_na_terra = BooleanField('Céu na Terra')
    rpg_supremacia = BooleanField('Supremacia')
    rpg_parte_1 = BooleanField('??? Parte 1')
    rpg_parte_2 = BooleanField('??? Parte 2')
    rpg_planoB = BooleanField('Plano B')

    def validate_email(self, email):
        if current_user.email != email.data:
            cadastrado = Usuario.query.filter_by(email=email.data).first()
            if cadastrado:
                raise ValidationError('E-mail já cadastrado. Faça login ou crie uma conta com outro e-mail. ')


class FormCriarPost(FlaskForm):
    corpo = TextAreaField('Escreva seu post aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Enviar Post')