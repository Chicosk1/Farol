# Imagem do back-end do Farol, usada no desenvolvimento e nos testes.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# As dependências vêm primeiro: o Docker reaproveita esta camada enquanto o pyproject.toml não muda.
COPY pyproject.toml ./
RUN pip install ".[dev]" && rm -rf build ./*.egg-info

# Usuário sem privilégios, com o mesmo UID do usuário da máquina, para que os arquivos criados
# na pasta montada (migrações, por exemplo) não fiquem com dono root.
ARG UID=1000
# A pasta /arquivos guarda os PDFs e as importações; o volume do Compose herda este dono.
RUN useradd --uid "${UID}" --create-home farol \
    && mkdir /arquivos \
    && chown farol /arquivos
COPY --chown=farol . .
USER farol

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
