# Imagem do front-end do Farol para desenvolvimento e testes: servidor do Vite com recarga automática.
FROM node:24-slim

WORKDIR /app
RUN chown node:node /app
USER node

# As dependências vêm primeiro: o Docker reaproveita esta camada enquanto o package-lock.json não muda.
COPY --chown=node:node package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY --chown=node:node . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
