# Imagen base para Node.js
FROM node:20-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de paquetes e instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer el puerto de Vite
EXPOSE 5173

# Comando para desarrollo
CMD ["npm", "run", "dev", "--", "--host"]
