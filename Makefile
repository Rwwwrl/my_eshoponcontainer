# DEV
build_dev:
	docker-compose -f docker-compose.dev.yml build

up_dev:
	docker-compose -f docker-compose.dev.yml up -d

down_dev:
	docker-compose -f docker-compose.dev.yml down



# LOCAL PROD
build_local_prod:
	docker-compose -f docker-compose.prod.yml -f docker-compose.local_prod.yml build

up_local_prod:
	docker-compose -f docker-compose.prod.yml -f docker-compose.local_prod.yml up -d

down_local_prod:
	docker-compose -f docker-compose.prod.yml -f docker-compose.local_prod.yml down



# PROD
dpull:
	docker-compose -f docker-compose.prod.yml pull

up_prod:
	docker-compose -f docker-compose.prod.yml up -d

down_prod:
	docker-compose -f docker-compose.prod.yml down



# TESTS
build_tests:
	docker-compose -f docker-compose.tests.yml build

up_tests:
	docker-compose -f docker-compose.tests.yml up

down_tests:
	docker-compose -f docker-compose.tests.yml down


# UTILS
create_or_renew_ssl_certificates:
	docker-compose -f docker-compose.ssl_certificates.yml build
	docker-compose -f docker-compose.ssl_certificates.yml up -d
	@sleep 3
	@echo
	@echo "INFO: certbot logs:"
	@docker logs certbot
	@echo
	docker-compose -f docker-compose.ssl_certificates.yml down
	@# TODO, пусть это будет пока что просто ввиде предупреждающей строки
	@echo
	@echo "INFO: если запущен prod nginx контейнер, то его нужно перезапустить, чтобы подтянуть новые сертификаты.\nВыполните 'sudo docker exec -it nginx nginx -s reload'."
	@echo