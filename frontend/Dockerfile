FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN npm install -D tailwindcss postcss autoprefixer


COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]
