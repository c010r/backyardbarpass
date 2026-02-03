#!/bin/bash

# Este script ayuda a obtener los certificados iniciales de Let's Encrypt
# Asegúrate de haber editado nginx.conf con tu dominio real antes de correrlo.

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose no está instalado.' >&2
  exit 1
fi

domains=(backyardbar.uy) # <--- CAMBIA ESTO POR TU DOMINIO
rsa_key_size=4096
data_path="./certbot"
email="admin@backyardbar.uy" # <--- CAMBIA ESTO POR TU EMAIL
staging=0 # Pon en 1 para probar sin gastar límites de Let's Encrypt

if [ -d "$data_path" ]; then
  read -p "Ya existen datos para certbot. ¿Deseas borrarlos y empezar de cero? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Descargando parámetros SSL recomendados..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
fi

echo "### Iniciando nginx..."
docker-compose -f docker-compose.prod.yml up --force-recreate -d nginx

echo "### Solicitando certificados a Let's Encrypt para $domains..."
# Unir dominios para el comando certbot
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Seleccionar email
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Modo staging si se solicita
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot

echo "### Recargando nginx..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
