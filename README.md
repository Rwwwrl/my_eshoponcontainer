https://www.notion.so/rwwwrl/eshoponcontainers-b1c5adea1aed4e96bcaf3cecb04a337b?pvs=4

## Deploy

1. создаем _ssl сертификаты_:

   ```bash
   make create_or_renew_ssl_certificates
   ```

2. поднимаем приложение:
   ```bash
   make up_prod
   ```

## Обновление _ssl сертификатов_

    1.
    ```bash
    make create_or_renew_ssl_certificates
    ```

    2. **если** приложение запущено, то нужно, чтобы nginx перечитал конфигурацию
    ```bash
    make nginx_reload
    ```
