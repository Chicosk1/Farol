"""Modelos do módulo contas (spec 001)."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


def normalizar_email(email: str) -> str:
    """E-mail sem espaços e em minúsculas, para não haver duas contas da mesma pessoa."""
    return (email or "").strip().lower()


class Perfil(models.TextChoices):
    """Papéis de uma pessoa no Farol (ACE-RF-03)."""

    ALUNO = "aluno", "Aluno"
    PROFESSOR = "professor", "Professor"
    COORDENACAO = "coordenacao", "Coordenação"
    ADMIN = "admin", "Administrador"


class GerenciadorDePessoas(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email: str, nome: str, **campos) -> "Pessoa":
        """Cria uma pessoa sem senha utilizável: entra pela conta institucional (ACE-RF-02)."""
        email = normalizar_email(email)
        if not email:
            raise ValueError("A pessoa precisa de um e-mail institucional.")
        campos.pop("password", None)
        pessoa = self.model(email=email, nome=nome, **campos)
        pessoa.set_unusable_password()
        pessoa.save(using=self._db)
        return pessoa

    def create_superuser(
        self, email: str, nome: str, password: str | None = None, **campos
    ) -> "Pessoa":
        """Cria uma pessoa da equipe com todas as permissões, ignorando a senha (ACE-RF-02)."""
        campos.setdefault("is_staff", True)
        campos.setdefault("is_superuser", True)
        return self.create_user(email, nome, **campos)


class Pessoa(AbstractBaseUser, PermissionsMixin):
    """Quem usa o Farol: aluno, professor, coordenação ou administração.

    É o modelo de usuário do Django desde a primeira migração. Não guarda senha (ACE-RF-02):
    o campo `password` herdado do Django só contém a marca de "senha inutilizável".
    Uma pessoa tem um ou mais perfis e escolhe o ativo ao entrar (ACE-RF-03).
    """

    email = models.EmailField("e-mail institucional", unique=True)
    nome = models.CharField("nome", max_length=150)
    is_active = models.BooleanField("ativa", default=True)
    is_staff = models.BooleanField("equipe do Farol", default=False)
    perfis = ArrayField(
        models.CharField(max_length=20, choices=Perfil.choices),
        verbose_name="perfis",
        default=list,
        blank=True,
    )
    criada_em = models.DateTimeField("criada em", default=timezone.now)

    objects = GerenciadorDePessoas()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        verbose_name = "pessoa"
        verbose_name_plural = "pessoas"

    def __str__(self) -> str:
        return f"{self.nome} <{self.email}>"

    def save(self, *args, **kwargs) -> None:
        self.email = normalizar_email(self.email)
        super().save(*args, **kwargs)

    def set_password(self, raw_password: str | None) -> None:
        """Nunca grava uma senha: o Farol não cria nem guarda senhas próprias (ACE-RF-02)."""
        self.set_unusable_password()
